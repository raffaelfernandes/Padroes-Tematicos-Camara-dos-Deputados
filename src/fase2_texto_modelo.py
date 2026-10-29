"""
fase2_texto_modelo.py

Fase 2 do TCC: define o texto que cada proposição leva para o modelo.

1. Aplica o critério de ementa formulaica (fase2_criterio_formulaicas.py) à base.
2. Para cada formulaica, tenta o fallback na ordem:
     ementaDetalhada (se preenchida e não formulaica)
     -> início do inteiro teor (PDF em urlInteiroTeor)
     -> sem_texto (mantém a ementa e marca)
3. Cria as colunas:
     eh_formulaica, texto_modelo, fonte_texto, id_texto_unico
   id_texto_unico agrupa proposições com o mesmo texto_modelo, para que a
   Fase 3 ajuste o BERTopic só nos textos únicos.

Uso:
    uv add pymupdf
    uv run python src/fase2_texto_modelo.py --base data/processed/base_proposicoes_20261027.parquet

    --K 1                  limiar de palavras de conteúdo (padrão 1)
    --n-chars 1000         tamanho do trecho do inteiro teor
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

CABECALHO_FIM = re.compile(
    r"(o\s+congresso\s+nacional\s+decreta\s*:|"
    r"as\s+mesas\s+da\s+c[âa]mara\s+dos\s+deputados\s+e\s+do\s+senado\s+federal.{0,200}?promulgam.{0,80}?:)",
    re.IGNORECASE | re.DOTALL,
)
JUSTIFICACAO = re.compile(r"\bjustifica[çc][ãa]o\b|\bjustificativa\b", re.IGNORECASE)
CABECA_PAGINA = re.compile(
    r"(c[âa]mara dos deputados|apresenta[çc][ãa]o:\s*\S+|assinado eletronicamente.*?$|"
    r"para verificar a assinatura.*?$|\*cd\d+\*|documento eletr[ôo]nico.*?$|"
    r"autentica[çc][ãa]o.*?$|https?://\S+)",
    re.IGNORECASE | re.MULTILINE,
)


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


def extrair_trecho(pdf: Path, n_chars: int) -> tuple[str, str]:
    """Devolve (trecho, status). status: ok, curto, sem_texto, erro."""
    import pymupdf

    try:
        with pymupdf.open(pdf) as doc:
            texto = "\n".join(p.get_text() for p in doc)
    except Exception:
        return "", "erro"
    texto = CABECA_PAGINA.sub(" ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    if len(texto) < 50:
        return "", "sem_texto"            # PDF escaneado ou vazio; sem OCR por decisão
    m = CABECALHO_FIM.search(texto)
    corpo = texto[m.end():] if m else texto
    # Prioriza o articulado; se ele for curto, completa com o início da justificação.
    j = JUSTIFICACAO.search(corpo)
    articulado = corpo[:j.start()] if j else corpo
    trecho = articulado.strip()
    if len(trecho) < n_chars and j:
        trecho = (trecho + " " + corpo[j.end():].strip()).strip()
    trecho = trecho[:n_chars]
    # Corta na última frase completa, se não perder muito.
    corte = trecho.rfind(". ")
    if corte > 0.6 * len(trecho):
        trecho = trecho[:corte + 1]
    return trecho, ("ok" if len(trecho) >= 200 else "curto")


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--saida", default="data/processed", type=Path)
    ap.add_argument("--pdfs", default="data/raw/inteiro_teor", type=Path)
    ap.add_argument("--K", type=int, default=1)
    ap.add_argument("--n-chars", type=int, default=1000)
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

    base["texto_modelo"] = base["ementa"]
    base["fonte_texto"] = "ementa"
    base["status_inteiro_teor"] = pd.NA

    # 2a. ementaDetalhada --------------------------------------------------------
    usa_det = base["eh_formulaica"] & base["ementaDetalhada"].str.len().gt(0) & \
        ~base["ementaDetalhada"].map(lambda e: eh_formulaica(e, a.K))
    base.loc[usa_det, "texto_modelo"] = base.loc[usa_det, "ementaDetalhada"]
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
            trechos.append((i, "", "falha_download"))
            continue
        t, st = extrair_trecho(p, a.n_chars)
        trechos.append((i, t, st))
    tr = pd.DataFrame(trechos, columns=["id", "trecho", "status"])
    if len(tr):
        tr["id"] = tr["id"].astype(base["id"].dtype)
        base = base.merge(tr, on="id", how="left")
        ok = base["status"].isin(["ok", "curto"]) & base["trecho"].fillna("").str.len().gt(0)
        # Mantém a ementa na frente: ela traz a referência legal, e o trecho traz o conteúdo.
        base.loc[ok, "texto_modelo"] = base.loc[ok, "ementa"] + " " + base.loc[ok, "trecho"]
        base.loc[ok, "fonte_texto"] = "inteiro_teor"
        base.loc[base["status"].notna(), "status_inteiro_teor"] = base["status"]
        base = base.drop(columns=["trecho", "status"])

    resto = base["eh_formulaica"] & base["fonte_texto"].eq("ementa")
    base.loc[resto, "fonte_texto"] = "sem_texto"

    # 3. Textos únicos -----------------------------------------------------------
    norm = base["texto_modelo"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip().str.rstrip(".")
    base["id_texto_unico"] = pd.factorize(norm)[0]

    # Saídas --------------------------------------------------------------------
    suf = date.today().strftime("%Y%m%d")
    base.to_parquet(a.saida / f"base_fase2_{suf}.parquet", index=False)

    it = base[base["fonte_texto"] == "inteiro_teor"]
    it.sample(min(30, len(it)), random_state=42)[["id", "ementa", "texto_modelo"]] \
        .to_csv(a.saida / f"inteiro_teor_amostra_{suf}.csv", index=False)

    vc = base["fonte_texto"].value_counts()
    st = base["status_inteiro_teor"].value_counts(dropna=True)
    comp = base.groupby("fonte_texto")["texto_modelo"].apply(lambda s: s.str.len().median())
    n_unicos = base["id_texto_unico"].nunique()
    linhas = [
        f"# Relatório da Fase 2\n",
        f"Gerado em {date.today().isoformat()} | K = {a.K} | trecho do inteiro teor = {a.n_chars} caracteres\n",
        f"- Formulaicas: {n_form} ({n_form / len(base):.2%})",
        f"- Resolvidas pela ementaDetalhada: {int(usa_det.sum())}",
        f"- Resolvidas pelo inteiro teor: {int(vc.get('inteiro_teor', 0))}",
        f"- Sem texto útil: {int(vc.get('sem_texto', 0))} ({vc.get('sem_texto', 0) / max(n_form, 1):.1%} das formulaicas)",
        f"- Textos únicos para o ajuste do modelo: {n_unicos} de {len(base)}",
        "\n## Fonte do texto\n",
        "| fonte_texto | n | comprimento mediano (caracteres) |",
        "| --- | --- | --- |",
        *[f"| {k} | {v} | {comp.get(k, 0):.0f} |" for k, v in vc.items()],
        "\n## Status do inteiro teor\n",
        "| status | n |", "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in st.items()],
        "\nConfira à mão os trechos em inteiro_teor_amostra_*.csv antes de seguir para a Fase 3.",
    ]
    (a.saida / f"relatorio_fase2_{suf}.md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()