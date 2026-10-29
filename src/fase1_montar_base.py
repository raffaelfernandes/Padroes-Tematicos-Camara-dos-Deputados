"""
montar_base_proposicoes.py

Monta a base do TCC a partir dos arquivos anuais do portal de Dados Abertos
da Câmara dos Deputados:

    proposicoes-{ano}.csv        uma linha por proposição
    proposicoesTemas-{ano}.csv   uma linha por (proposição, tema oficial)
    proposicoesAutores-{ano}.csv uma linha por (proposição, autor)

Saídas (em --saida, padrão data/processed):

    base_proposicoes.parquet  uma linha por proposição do recorte, com texto,
                              temas oficiais (listas) e primeiro autor
    temas_long.parquet        (id, codTema, tema, relevancia) -> gabarito do BCubed
    autores_long.parquet      todas as assinaturas das proposições do recorte
    relatorio_coleta.md       números da Fase 1 e checagens de qualidade

Uso:
    uv run python src/fase1_montar_base.py
    uv run python src/fase1_montar_base.py --inicio 2019-02-01 --fim 2026-09-30
    uv run python src/fase1_montar_base.py --sem-download   # só usa o que já está em data/raw

Dependências: pandas, pyarrow, requests
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

URL_ARQUIVO = "https://dadosabertos.camara.leg.br/arquivos/{nome}/csv/{nome}-{ano}.csv"
ARQUIVOS = ("proposicoes", "proposicoesTemas", "proposicoesAutores")
TIPOS_PADRAO = ("PL", "PEC", "PLP")

# Colunas mínimas que cada arquivo precisa ter. Se a Câmara mudar algum nome,
# o script para aqui e diz exatamente o que faltou.
COLUNAS_OBRIGATORIAS = {
    "proposicoes": ["id", "siglaTipo", "numero", "ano", "ementa", "dataApresentacao"],
    "proposicoesTemas": ["uriProposicao", "codTema", "tema"],
    "proposicoesAutores": ["nomeAutor", "tipoAutor", "ordemAssinatura"],
}

# Colunas de proposicoes que vale carregar.
COLUNAS_PROPOSICOES = [
    "id", "uri", "siglaTipo", "numero", "ano", "codTipo", "descricaoTipo",
    "ementa", "ementaDetalhada", "keywords", "dataApresentacao",
    "urlInteiroTeor", "uriPropPrincipal", "uriPropAnterior", "uriPropPosterior",
    "ultimoStatus_dataHora", "ultimoStatus_siglaOrgao",
    "ultimoStatus_descricaoTramitacao", "ultimoStatus_descricaoSituacao",
    "ultimoStatus_idSituacao", "ultimoStatus_regime", "ultimoStatus_apreciacao",
]

RE_ID_URI = re.compile(r"/proposicoes/(\d+)")


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def baixar(nome: str, ano: int, destino: Path, refazer: bool, tentativas: int = 4) -> Path | None:
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / f"{nome}-{ano}.csv"
    if arquivo.exists() and arquivo.stat().st_size > 0 and not refazer:
        print(f"  [cache] {arquivo.name}")
        return arquivo

    url = URL_ARQUIVO.format(nome=nome, ano=ano)
    for t in range(1, tentativas + 1):
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                if r.status_code == 404:
                    print(f"  [404]   {url}")
                    return None
                r.raise_for_status()
                tmp = arquivo.with_suffix(".part")
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(chunk_size=1 << 20):
                        f.write(bloco)
                tmp.replace(arquivo)
            print(f"  [ok]    {arquivo.name} ({arquivo.stat().st_size / 1e6:.1f} MB)")
            return arquivo
        except requests.RequestException as e:
            espera = 5 * t
            print(f"  [erro]  {nome}-{ano} tentativa {t}/{tentativas}: {e}. Nova tentativa em {espera}s")
            time.sleep(espera)
    print(f"  [falha] {nome}-{ano} não foi baixado")
    return None


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def ler_csv(caminho: Path) -> pd.DataFrame:
    """Os CSVs da Câmara usam ';' e UTF-8 com BOM. Lê tudo como texto para
    não perder zeros, ids grandes ou datas em formatos diferentes."""
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(caminho, sep=";", dtype=str, encoding=enc,
                             keep_default_na=False, na_values=[""])
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"Não consegui decodificar {caminho}")
    df.columns = [c.strip() for c in df.columns]
    return df


def checar_colunas(df: pd.DataFrame, nome: str, origem: Path) -> None:
    faltando = [c for c in COLUNAS_OBRIGATORIAS[nome] if c not in df.columns]
    if nome == "proposicoesAutores" and "idProposicao" not in df.columns and "uriProposicao" not in df.columns:
        faltando.append("idProposicao ou uriProposicao")
    if faltando:
        sys.exit(
            f"\n[ERRO] {origem.name} não tem as colunas {faltando}.\n"
            f"Colunas encontradas: {list(df.columns)}\n"
            f"Ajuste COLUNAS_OBRIGATORIAS ou o mapeamento no script."
        )


def ler_todos(nome: str, anos: list[int], raw: Path, baixar_arquivos: bool, refazer_ano_atual: bool) -> pd.DataFrame:
    print(f"\n{nome}")
    partes = []
    ano_atual = date.today().year
    for ano in anos:
        pasta = raw / nome
        if baixar_arquivos:
            caminho = baixar(nome, ano, pasta, refazer=(refazer_ano_atual and ano == ano_atual))
        else:
            caminho = pasta / f"{nome}-{ano}.csv"
            caminho = caminho if caminho.exists() else None
            print(f"  [local] {nome}-{ano}.csv {'ok' if caminho else 'NÃO ENCONTRADO'}")
        if caminho is None:
            continue
        df = ler_csv(caminho)
        checar_colunas(df, nome, caminho)
        df["arquivo_ano"] = ano
        partes.append(df)
    if not partes:
        sys.exit(f"[ERRO] Nenhum arquivo de {nome} disponível.")
    return pd.concat(partes, ignore_index=True)


def id_da_uri(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.extract(RE_ID_URI, expand=False)


# --------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------

def preparar_proposicoes(df: pd.DataFrame, tipos: tuple[str, ...], inicio: pd.Timestamp, fim: pd.Timestamp) -> pd.DataFrame:
    cols = [c for c in COLUNAS_PROPOSICOES if c in df.columns] + ["arquivo_ano"]
    df = df[cols].copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["dataApresentacao"] = pd.to_datetime(df["dataApresentacao"], errors="coerce")
    df["siglaTipo"] = df["siglaTipo"].str.strip()

    n0 = len(df)
    df = df[df["siglaTipo"].isin(tipos)]
    df = df[(df["dataApresentacao"] >= inicio) & (df["dataApresentacao"] <= fim)]
    # O mesmo id pode aparecer em mais de um arquivo anual; fica a versão do arquivo mais novo.
    df = df.sort_values("arquivo_ano").drop_duplicates("id", keep="last")
    print(f"\nProposições: {n0} linhas brutas -> {len(df)} no recorte ({', '.join(tipos)})")

    df["legislatura"] = pd.cut(
        df["dataApresentacao"],
        bins=[pd.Timestamp("2019-02-01"), pd.Timestamp("2023-02-01"), pd.Timestamp("2027-02-01")],
        labels=[56, 57], right=False,
    ).astype("Int64")
    df["ano_mes"] = df["dataApresentacao"].dt.to_period("M").astype(str)
    for c in ("ementa", "ementaDetalhada"):
        if c in df.columns:
            df[c] = df[c].fillna("").str.strip()
    df["len_ementa"] = df["ementa"].str.len()
    df["tem_ementaDetalhada"] = df.get("ementaDetalhada", pd.Series("", index=df.index)).str.len() > 0
    if "uriPropPrincipal" in df.columns:
        df["eh_apensada"] = df["uriPropPrincipal"].notna() & (df["uriPropPrincipal"].astype(str).str.len() > 0)
        df["idPropPrincipal"] = pd.to_numeric(id_da_uri(df["uriPropPrincipal"]), errors="coerce").astype("Int64")
    return df.drop(columns=["arquivo_ano"])


def preparar_temas(df: pd.DataFrame, ids: set) -> pd.DataFrame:
    df = df.copy()
    df["id"] = pd.to_numeric(id_da_uri(df["uriProposicao"]), errors="coerce").astype("Int64")
    df["codTema"] = pd.to_numeric(df["codTema"], errors="coerce").astype("Int64")
    cols = ["id", "codTema", "tema"] + (["relevancia"] if "relevancia" in df.columns else [])
    df = df[cols].dropna(subset=["id", "codTema"])
    df = df[df["id"].isin(ids)].drop_duplicates(["id", "codTema"])
    return df


def preparar_autores(df: pd.DataFrame, ids: set) -> pd.DataFrame:
    df = df.copy()
    if "idProposicao" in df.columns:
        df["id"] = pd.to_numeric(df["idProposicao"], errors="coerce").astype("Int64")
    else:
        df["id"] = pd.to_numeric(id_da_uri(df["uriProposicao"]), errors="coerce").astype("Int64")
    df["ordemAssinatura"] = pd.to_numeric(df["ordemAssinatura"], errors="coerce")
    if "proponente" in df.columns:
        df["proponente"] = pd.to_numeric(df["proponente"], errors="coerce")
    df = df[df["id"].isin(ids)]
    manter = [c for c in [
        "id", "idDeputadoAutor", "uriAutor", "nomeAutor", "codTipoAutor", "tipoAutor",
        "siglaPartidoAutor", "siglaUFAutor", "ordemAssinatura", "proponente",
    ] if c in df.columns]
    df = df[manter].drop_duplicates()
    return df


def primeiro_autor(autores: pd.DataFrame) -> pd.DataFrame:
    """Primeiro signatário: menor ordemAssinatura, preferindo proponente == 1."""
    a = autores.copy()
    a["_prop"] = -a["proponente"].fillna(0) if "proponente" in a.columns else 0
    a["_ordem"] = a["ordemAssinatura"].fillna(1e9)
    a = a.sort_values(["id", "_prop", "_ordem"]).drop_duplicates("id", keep="first")
    renome = {
        "nomeAutor": "autor1_nome", "tipoAutor": "autor1_tipo",
        "idDeputadoAutor": "autor1_idDeputado", "siglaPartidoAutor": "autor1_partido",
        "siglaUFAutor": "autor1_uf",
    }
    a = a.rename(columns=renome)
    cols = ["id"] + [v for k, v in renome.items() if v in a.columns]
    a = a[cols]
    a["autor1_eh_deputado"] = a["autor1_tipo"].fillna("").str.startswith("Deputado")
    return a


def montar_base(prop: pd.DataFrame, temas: pd.DataFrame, autores: pd.DataFrame) -> pd.DataFrame:
    temas_agg = (temas.sort_values(["id", "codTema"])
                 .groupby("id")
                 .agg(temas_cod=("codTema", lambda s: [int(x) for x in s]),
                      temas_nome=("tema", list))
                 .reset_index())
    temas_agg["n_temas"] = temas_agg["temas_cod"].str.len()

    n_aut = autores.groupby("id").size().rename("n_autores").reset_index()
    a1 = primeiro_autor(autores)

    base = (prop.merge(temas_agg, on="id", how="left", validate="one_to_one")
                .merge(a1, on="id", how="left", validate="one_to_one")
                .merge(n_aut, on="id", how="left", validate="one_to_one"))
    base["n_temas"] = base["n_temas"].fillna(0).astype(int)
    base["tem_tema"] = base["n_temas"] > 0
    base["n_autores"] = base["n_autores"].fillna(0).astype(int)
    base["temas_cod"] = base["temas_cod"].apply(lambda x: x if isinstance(x, list) else [])
    base["temas_nome"] = base["temas_nome"].apply(lambda x: x if isinstance(x, list) else [])
    return base


# --------------------------------------------------------------------------
# Relatório
# --------------------------------------------------------------------------

def tabela_md(df: pd.DataFrame) -> str:
    df = df.reset_index()
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |",
              "| " + " | ".join(["---"] * len(df.columns)) + " |"]
    for _, r in df.iterrows():
        linhas.append("| " + " | ".join(str(v) for v in r.values) + " |")
    return "\n".join(linhas)


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def relatorio(base: pd.DataFrame, temas: pd.DataFrame, autores: pd.DataFrame,
              inicio, fim, caminho: Path) -> None:
    n = len(base)
    out = [f"# Relatório de coleta\n",
           f"Gerado em {date.today().isoformat()} | recorte {inicio.date()} a {fim.date()} | N = {n}\n"]

    out.append("## Volume por ano e tipo\n")
    vol = pd.crosstab(base["dataApresentacao"].dt.year, base["siglaTipo"], margins=True, margins_name="Total")
    out.append(tabela_md(vol) + "\n")

    out.append("## Cobertura de temas oficiais (codTema)\n")
    out.append(f"- Com ao menos um tema: {pct(base['tem_tema'].mean())}")
    out.append(f"- Temas distintos: {temas['codTema'].nunique()}")
    com = base[base["tem_tema"]]
    if len(com):
        out.append(f"- Média de temas por proposição (entre as que têm tema): {com['n_temas'].mean():.2f}")
    out.append("\nCobertura mês a mês (use para decidir até onde o BCubed é avaliado):\n")
    cob = base.groupby("ano_mes").agg(n=("id", "size"), cobertura=("tem_tema", "mean"))
    cob["cobertura"] = cob["cobertura"].map(pct)
    out.append(tabela_md(cob) + "\n")

    out.append("## Distribuição dos temas\n")
    dist = temas["tema"].value_counts().rename("n_proposicoes").to_frame()
    out.append(tabela_md(dist) + "\n")

    out.append("## Texto\n")
    q = base["len_ementa"].quantile([.1, .5, .9]).round(0).astype(int)
    out.append(f"- Comprimento da ementa (caracteres): p10 = {q[.1]}, mediana = {q[.5]}, p90 = {q[.9]}")
    out.append(f"- Ementas vazias: {(base['len_ementa'] == 0).sum()}")
    out.append(f"- Ementas com até 40 caracteres: {pct((base['len_ementa'] <= 40).mean())}")
    out.append(f"- ementaDetalhada preenchida: {pct(base['tem_ementaDetalhada'].mean())}")
    dup = base["ementa"].str.lower().str.strip().duplicated(keep=False)
    out.append(f"- Proposições com ementa idêntica a outra: {dup.sum()} ({pct(dup.mean())})")
    if "eh_apensada" in base.columns:
        out.append(f"- Apensadas (têm uriPropPrincipal): {pct(base['eh_apensada'].mean())}")

    out.append("\n## Autoria\n")
    out.append(f"- Proposições sem autor no arquivo de autores: {(base['n_autores'] == 0).sum()}")
    tipos = base["autor1_tipo"].fillna("(sem autor)").value_counts().rename("n").to_frame()
    out.append("\nTipo do primeiro autor:\n")
    out.append(tabela_md(tipos) + "\n")
    dep = base[base["autor1_eh_deputado"].fillna(False)]
    if "autor1_partido" in base.columns:
        out.append(f"- Primeiro autor deputado sem partido preenchido: {dep['autor1_partido'].isna().sum()}")
        part = dep["autor1_partido"].value_counts().rename("n_proposicoes").to_frame()
        out.append("\nProposições por partido do primeiro autor (só deputados):\n")
        out.append(tabela_md(part) + "\n")

    out.append("## Checagens\n")
    out.append(f"- ids duplicados na base: {base['id'].duplicated().sum()} (esperado 0)")
    out.append(f"- Linhas de tema sem proposição correspondente foram descartadas no join")
    out.append(f"- Linhas de autoria do recorte: {len(autores)}")

    caminho.write_text("\n".join(out), encoding="utf-8")
    print(f"Relatório salvo em {caminho}")


# --------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inicio", default="2019-02-01", help="início do recorte (data de apresentação)")
    p.add_argument("--fim", default="2026-09-30", help="fim do recorte (inclusive)")
    p.add_argument("--tipos", default=",".join(TIPOS_PADRAO))
    p.add_argument("--raw", default="data/raw", type=Path)
    p.add_argument("--saida", default="data/processed", type=Path)
    p.add_argument("--sem-download", action="store_true", help="não baixa nada, usa só os arquivos em --raw")
    p.add_argument("--manter-ano-atual", action="store_true",
                   help="não rebaixa o arquivo do ano corrente (por padrão ele é rebaixado)")
    args = p.parse_args()

    inicio = pd.Timestamp(args.inicio)
    fim = pd.Timestamp(args.fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    tipos = tuple(t.strip().upper() for t in args.tipos.split(","))
    # Inclui o ano seguinte ao fim: proposições podem cair num arquivo vizinho.
    anos = list(range(inicio.year, min(fim.year + 1, date.today().year) + 1))

    brutos = {
        nome: ler_todos(nome, anos, args.raw, not args.sem_download, not args.manter_ano_atual)
        for nome in ARQUIVOS
    }

    prop = preparar_proposicoes(brutos["proposicoes"], tipos, inicio, fim)
    ids = set(prop["id"].dropna())
    temas = preparar_temas(brutos["proposicoesTemas"], ids)
    autores = preparar_autores(brutos["proposicoesAutores"], ids)
    base = montar_base(prop, temas, autores)

    args.saida.mkdir(parents=True, exist_ok=True)
    sufixo = date.today().strftime("%Y%m%d")
    base.to_parquet(args.saida / f"base_proposicoes_{sufixo}.parquet", index=False)
    temas.to_parquet(args.saida / f"temas_long_{sufixo}.parquet", index=False)
    autores.to_parquet(args.saida / f"autores_long_{sufixo}.parquet", index=False)
    relatorio(base, temas, autores, inicio, fim, args.saida / f"relatorio_coleta_{sufixo}.md")

    print(f"\nBase: {len(base)} proposições | com tema: {pct(base['tem_tema'].mean())} | "
          f"primeiro autor deputado: {pct(base['autor1_eh_deputado'].fillna(False).mean())}")
    print(f"Arquivos em {args.saida.resolve()}")


if __name__ == "__main__":
    main()