"""
fase2_texto_modelo.py

Fase 2 do TCC: define o texto que cada proposição leva para o modelo.

1. Aplica o critério de ementa formulaica (fase2_criterio_formulaicas.py) à base.
2. Para cada formulaica, tenta o fallback na ordem:
     ementaDetalhada (se preenchida e não formulaica)
     -> início da JUSTIFICAÇÃO do inteiro teor (PDF em urlInteiroTeor);
        se não houver justificação aproveitável, o articulado sem as fórmulas legislativas
     -> sem_texto (mantém a ementa e marca)
   O articulado ("passa a vigorar com a seguinte redação", "Esta Lei entra em vigor...")
   é quase igual em todos os projetos e fez as formulaicas se agruparem pelo formato
   na primeira rodada da Fase 3. A justificação descreve o assunto em prosa.
   Nas proposições resolvidas pelo inteiro teor, o texto do modelo é só o trecho
   (a ementa formulaica não informa o tema); --manter-ementa volta ao formato antigo.
3. Normaliza textos escritos todos em maiúsculas (o BERTimbau diferencia caixa e,
   na primeira rodada, juntou as ementas em caixa alta num tópico próprio).
4. Cria as colunas:
     eh_formulaica, texto_modelo, fonte_texto, parte_inteiro_teor, caixa_alta, id_texto_unico
   id_texto_unico agrupa proposições com o mesmo texto_modelo, para que a
   Fase 3 ajuste o BERTopic só nos textos únicos.

Uso:
    uv add pymupdf
    uv run python src/fase2_texto_modelo.py --base data/processed/base_proposicoes_20261027.parquet

    --K 1                  limiar de palavras de conteúdo (padrão 1)
    --n-chars 500          tamanho do trecho do inteiro teor
    --parte justificacao   parte do inteiro teor usada (justificacao ou articulado)
    --sem-download         usa só os PDFs já baixados em data/raw/inteiro_teor

Saídas em data/processed:
    base_fase2_AAAAMMDD.parquet
    relatorio_fase2_AAAAMMDD.md
    inteiro_teor_amostra_AAAAMMDD.csv   (trechos extraídos, para conferir à mão)
"""

from __future__ import annotations

import argparse
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from fase2_criterio_formulaicas import eh_formulaica
from texto_referencias import mascarar_referencias

CABECALHO_FIM = re.compile(
    r"(o\s+congresso\s+nacional\s+decreta\s*:|"
    r"as\s+mesas\s+da\s+c[âa]mara\s+dos\s+deputados\s+e\s+do\s+senado\s+federal.{0,200}?promulgam.{0,80}?:)",
    re.IGNORECASE | re.DOTALL,
)
JUSTIFICACAO_TITULO = re.compile(r"\bJUSTIFICA[ÇC][ÃA]O\b|\bJUSTIFICATIVA\b")   # título, em maiúsculas
JUSTIFICACAO_QUALQUER = re.compile(r"\bjustifica[çc][ãa]o\b|\bjustificativa\b", re.IGNORECASE)
SALA_SESSOES = re.compile(r"sala\s+das\s+sess[õo]es", re.IGNORECASE)
SAUDACAO = re.compile(
    r"^\s*(senhor(a)?\s+presidente\s*,?|excelent[íi]ssim[oa][^,.]{0,80}[,.]|"
    r"nobres?\s+(pares|colegas|deputad[oa]s)\s*,?|senhor(a|es|as)?\s+deputad[oa]s?\s*,?)\s*",
    re.IGNORECASE,
)
# Linhas de cabeçalho, rodapé e assinatura que se repetem em todas as páginas
LINHA_LIXO = re.compile(
    r"^\s*(\*?CD\d+\*?|LexEdit|assinado\s+eletronicamente.*|para\s+verificar\s+a\s+assinatura.*|"
    r"documento\s+eletr[ôo]nico.*|na\s+forma\s+do\s+art\.?\s*102.*|da\s+mesa\s+n\.?\s*80.*|"
    r"(PL|PLP|PEC|PDL)\s*n\.?\s*[\d\.]+/\d{4}|apresenta[çc][ãa]o:.*|c[âa]mara\s+dos\s+deputados|"
    r"gabinete\s+d[oa]\s+.*|deputad[oa]\s+federal\s+.*|\d{1,3}|\d{4}-\d+|https?://\S+|"
    r"autentica[çc][ãa]o.*)\s*$",
    re.IGNORECASE,
)
PONTILHADO = re.compile(r"\.{3,}|…+")
# Endereço do gabinete, telefones, e-mails e links que aparecem no meio do texto
INLINE_LIXO = re.compile(
    r"C[âa]mara\s+dos\s+Deputados\s*[│|\-–]*\s*Anexo\s+[IVX]+.{0,250}?(?:\S+@camara\.leg\.br|(?:Fax\s*)?\(61\)\s*\d{4}[\-–]\d{4}(?!.{0,40}\(61\)))"
    r"|Anexo\s+[IVX]+\s*[–\-]\s*\d+\s*[º°]?\s*andar.{0,250}?(?:\S+@camara\.leg\.br|\(61\)\s*\d{4}[\-–]\d{4}(?!.{0,40}\(61\)))"
    r"|https?://\S+|\S+@camara\.leg\.br",
    re.I | re.S)
# Fórmulas do articulado, removidas quando o fallback precisa usá-lo
FORMULAS_ARTICULADO = [
    re.compile(p, re.IGNORECASE) for p in (
        r"esta\s+(lei|lei\s+complementar|emenda\s+constitucional)\s+entra\s+em\s+vigor[^.]*\.?",
        r"revogam-se\s+as\s+disposi[çc][õo]es\s+em\s+contr[áa]rio\.?",
        r"passa(m)?\s+a\s+vigorar\s+(com\s+a\s+seguinte\s+reda[çc][ãa]o|acrescid[oa]s?[^:]{0,120})\s*:?",
        r"fica(m)?\s+revogad[oa]s?", r"\(\s*NR\s*\)", r"\bart\.?\s*\d+[ºo°]?(-[A-Z])?\s*[\.\-–]?",
        r"§\s*\d+[ºo°]?", r"par[áa]grafo\s+[úu]nico\.?", r"\bcaput\b",
    )
]


def limpar_paginas(texto: str) -> str:
    linhas = [l for l in texto.splitlines() if not LINHA_LIXO.match(l)]
    t = " ".join(linhas)
    t = INLINE_LIXO.sub(" ", t)
    t = re.sub(r"[│|]", " ", t)
    t = PONTILHADO.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def eh_caixa_alta(t: str, limiar: float = 0.6) -> bool:
    letras = [c for c in t if c.isalpha()]
    return bool(letras) and sum(c.isupper() for c in letras) / len(letras) > limiar


def normalizar_caixa(t: str) -> str:
    """Texto quase todo em maiúsculas vira minúsculas, mantendo a inicial."""
    if not isinstance(t, str) or not eh_caixa_alta(t):
        return t
    t = t.lower()
    return t[:1].upper() + t[1:]


# --------------------------------------------------------------------------
# Inteiro teor
# --------------------------------------------------------------------------

def baixar_pdf(id_prop: int, url: str, pasta: Path, tentativas: int = 3) -> Path | None:
    destino = pasta / f"{id_prop}.pdf"
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    for t in range(1, tentativas + 1):
        try:
            r = requests.get(url, timeout=60, allow_redirects=True,
                             headers={"User-Agent": "TCC-UFPI-pesquisa-academica"})
            if r.status_code == 404:
                return None
            r.raise_for_status()
            if not r.content.startswith(b"%PDF"):
                return None
            destino.write_bytes(r.content)
            return destino
        except requests.RequestException:
            time.sleep(3 * t)
    return None


def extrair_trecho(pdf: Path, n_chars: int, parte: str = "justificacao") -> tuple[str, str, str]:
    """Devolve (trecho, status, parte_usada).
    status: ok, curto, sem_texto, erro. parte_usada: justificacao, articulado ou vazio."""
    import pymupdf

    try:
        with pymupdf.open(pdf) as doc:
            bruto = "\n".join(p.get_text() for p in doc)
    except Exception:
        return "", "erro", ""
    texto = limpar_paginas(bruto)
    if len(texto) < 50:
        return "", "sem_texto", ""            # PDF escaneado ou vazio; sem OCR por decisão
    m = CABECALHO_FIM.search(texto)
    ini_corpo = m.end() if m else 0
    j = JUSTIFICACAO_TITULO.search(texto, ini_corpo) or JUSTIFICACAO_QUALQUER.search(texto, ini_corpo)

    trecho, usada = "", ""
    if parte == "justificacao" and j:
        just = texto[j.end():]
        fim_s = SALA_SESSOES.search(just)
        just = just[:fim_s.start()] if fim_s else just
        anterior = None
        while anterior != just:                # remove saudações em sequência
            anterior, just = just, SAUDACAO.sub("", just, count=1)
        if len(just.strip()) >= 150:
            trecho, usada = just.strip(), "justificacao"
    if not trecho:
        art = texto[ini_corpo:(j.start() if j else None)]
        for rx in FORMULAS_ARTICULADO:
            art = rx.sub(" ", art)
        trecho, usada = re.sub(r"\s+", " ", art).strip(" .;:-–\"“”"), "articulado"

    trecho = trecho[:n_chars]
    corte = trecho.rfind(". ")                 # termina na última frase completa
    if corte > 0.6 * len(trecho):
        trecho = trecho[:corte + 1]
    return trecho, ("ok" if len(trecho) >= 200 else "curto"), usada


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--saida", default="data/processed", type=Path)
    ap.add_argument("--pdfs", default="data/raw/inteiro_teor", type=Path)
    ap.add_argument("--K", type=int, default=1)
    ap.add_argument("--n-chars", type=int, default=500)
    ap.add_argument("--parte", choices=["justificacao", "articulado"], default="justificacao")
    ap.add_argument("--manter-ementa", action="store_true",
                    help="põe a ementa formulaica na frente do trecho do inteiro teor (comportamento antigo)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sem-download", action="store_true")
    a = ap.parse_args()
    a.pdfs.mkdir(parents=True, exist_ok=True)
    a.saida.mkdir(parents=True, exist_ok=True)

    base = pd.read_parquet(a.base)
    for c in ("ementaDetalhada", "urlInteiroTeor"):
        if c not in base.columns:
            base[c] = ""
    base["ementa"] = base["ementa"].fillna("").str.strip()
    base["ementaDetalhada"] = base["ementaDetalhada"].fillna("").str.strip()

    # 1. Critério ---------------------------------------------------------------
    base["eh_formulaica"] = base["ementa"].map(lambda e: eh_formulaica(e, a.K))
    n_form = int(base["eh_formulaica"].sum())
    print(f"Formulaicas (K={a.K}): {n_form} de {len(base)} ({n_form / len(base):.2%})")

    base["caixa_alta"] = base["ementa"].map(eh_caixa_alta)
    print(f"Ementas em caixa alta (normalizadas): {int(base['caixa_alta'].sum())}")
    base["texto_modelo"] = base["ementa"].map(normalizar_caixa)
    base["fonte_texto"] = "ementa"
    base["status_inteiro_teor"] = pd.NA
    base["parte_inteiro_teor"] = pd.NA

    # 2a. ementaDetalhada --------------------------------------------------------
    usa_det = base["eh_formulaica"] & base["ementaDetalhada"].str.len().gt(0) & \
        ~base["ementaDetalhada"].map(lambda e: eh_formulaica(e, a.K))
    base.loc[usa_det, "texto_modelo"] = base.loc[usa_det, "ementaDetalhada"].map(normalizar_caixa)
    base.loc[usa_det, "fonte_texto"] = "ementaDetalhada"
    print(f"Resolvidas pela ementaDetalhada: {int(usa_det.sum())}")

    # 2b. Inteiro teor -----------------------------------------------------------
    pend = base[base["eh_formulaica"] & ~usa_det]
    pend = pend[pend["urlInteiroTeor"].fillna("").str.startswith("http")]
    print(f"Buscando inteiro teor de {len(pend)} proposições...")

    caminhos: dict[int, Path | None] = {}
    if a.sem_download:
        for i in pend["id"]:
            p = a.pdfs / f"{i}.pdf"
            caminhos[int(i)] = p if p.exists() else None
    else:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(baixar_pdf, int(r.id), r.urlInteiroTeor, a.pdfs): int(r.id)
                    for r in pend.itertuples()}
            for k, f in enumerate(as_completed(futs), 1):
                caminhos[futs[f]] = f.result()
                if k % 100 == 0:
                    print(f"  {k}/{len(futs)}")

    trechos = []
    for i, p in caminhos.items():
        if p is None:
            trechos.append((i, "", "falha_download", ""))
            continue
        t, st, usada = extrair_trecho(p, a.n_chars, a.parte)
        trechos.append((i, normalizar_caixa(t), st, usada))
    tr = pd.DataFrame(trechos, columns=["id", "trecho", "status", "parte"])
    if len(tr):
        tr["id"] = tr["id"].astype(base["id"].dtype)
        base = base.merge(tr, on="id", how="left")
        ok = base["status"].isin(["ok", "curto"]) & base["trecho"].fillna("").str.len().gt(0)
        # A ementa formulaica não informa o tema; na frente do trecho, ela só acrescenta ruído de formato
        # (rodada 2 da Fase 3). Por padrão, o texto do modelo é só o trecho do inteiro teor.
        if a.manter_ementa:
            base.loc[ok, "texto_modelo"] = base.loc[ok, "ementa"].map(normalizar_caixa) + " " + base.loc[ok, "trecho"]
        else:
            base.loc[ok, "texto_modelo"] = base.loc[ok, "trecho"]
        base.loc[ok, "fonte_texto"] = "inteiro_teor"
        base.loc[ok, "parte_inteiro_teor"] = base.loc[ok, "parte"]
        base.loc[base["status"].notna(), "status_inteiro_teor"] = base["status"]
        base = base.drop(columns=["trecho", "status", "parte"])

    resto = base["eh_formulaica"] & base["fonte_texto"].eq("ementa")
    base.loc[resto, "fonte_texto"] = "sem_texto"

    # 3. Texto do embedding: sem números e datas de referências legais ------------
    # O texto_modelo continua legível (leitura e rótulos); o embedding usa texto_embedding.
    base["texto_embedding"] = base["texto_modelo"].map(mascarar_referencias)
    n_mask = int((base["texto_embedding"] != base["texto_modelo"]).sum())
    print(f"Textos com referências legais removidas para o embedding: {n_mask}")

    # 4. Textos únicos (pelo texto do embedding) ---------------------------------
    norm = base["texto_embedding"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip().str.rstrip(".")
    base["id_texto_unico"] = pd.factorize(norm)[0]

    # Saídas --------------------------------------------------------------------
    suf = date.today().strftime("%Y%m%d")
    base.to_parquet(a.saida / f"base_fase2_{suf}.parquet", index=False)

    it = base[base["fonte_texto"] == "inteiro_teor"]
    it.sample(min(30, len(it)), random_state=42)[["id", "ementa", "parte_inteiro_teor", "texto_modelo", "texto_embedding"]] \
        .to_csv(a.saida / f"inteiro_teor_amostra_{suf}.csv", index=False)

    vc = base["fonte_texto"].value_counts()
    st = base["status_inteiro_teor"].value_counts(dropna=True)
    comp = base.groupby("fonte_texto")["texto_modelo"].apply(lambda s: s.str.len().median())
    n_unicos = base["id_texto_unico"].nunique()
    linhas = [
        f"# Relatório da Fase 2\n",
        f"Gerado em {date.today().isoformat()} | K = {a.K} | trecho do inteiro teor = {a.n_chars} caracteres "
        f"| parte preferida = {a.parte} | ementa na frente do trecho = {'sim' if a.manter_ementa else 'não'}\n",
        f"- Formulaicas: {n_form} ({n_form / len(base):.2%})",
        f"- Resolvidas pela ementaDetalhada: {int(usa_det.sum())}",
        f"- Resolvidas pelo inteiro teor: {int(vc.get('inteiro_teor', 0))}",
        f"- Sem texto útil: {int(vc.get('sem_texto', 0))} ({vc.get('sem_texto', 0) / max(n_form, 1):.1%} das formulaicas)",
        f"- Textos únicos para o ajuste do modelo: {n_unicos} de {len(base)}",
        f"- Ementas em caixa alta normalizadas: {int(base['caixa_alta'].sum())}",
        f"- Textos com números e datas de referências legais removidos para o embedding: {n_mask}",
        "\n## Fonte do texto\n",
        "| fonte_texto | n | comprimento mediano (caracteres) |",
        "| --- | --- | --- |",
        *[f"| {k} | {v} | {comp.get(k, 0):.0f} |" for k, v in vc.items()],
        "\n## Status do inteiro teor\n",
        "| status | n |", "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in st.items()],
        "\n## Parte do inteiro teor usada\n",
        "| parte | n |", "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in base["parte_inteiro_teor"].value_counts(dropna=True).items()],
        "\nConfira à mão os trechos em inteiro_teor_amostra_*.csv antes de seguir para a Fase 3.",
    ]
    (a.saida / f"relatorio_fase2_{suf}.md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()