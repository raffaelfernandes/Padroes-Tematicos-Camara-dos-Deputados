"""
avaliacao_humana.py

Extra da revisão final do TCC (14/11/2026). Avaliação humana independente dos tópicos pelo teste de
intrusão de documentos (Chang et al., 2009, "Reading tea leaves"), com uma nota de coerência.

Para cada tópico sorteado, o avaliador vê os 10 termos de c-TF-IDF e seis ementas: cinco do tópico e
uma de outro tópico do mesmo modelo (a intrusa), em ordem aleatória. Ele aponta a intrusa e dá uma
nota de coerência de 1 a 3. Se o tópico tem um assunto claro, a intrusa é fácil de achar; ao acaso,
acerta-se 1 em 6 (17%).

Entram 16 tópicos do BERTimbau e 8 do LDA com 66 tópicos (baseline), misturados e sem identificação do
modelo. Os termos dos dois saem do mesmo vetorizador e da mesma conta de c-TF-IDF, e as ementas são
sorteadas entre todas as substantivas do tópico (núcleo e reatribuídas), para a comparação ser justa.

Subcomandos (a partir de code/):
    uv run python src/extras/avaliacao_humana.py gerar
    uv run python src/extras/avaliacao_humana.py resumir anotacoes/avaliacao_humana_RESPOSTAS_<nome>.xlsx [outro.xlsx ...]

Arquivos:
    anotacoes/avaliacao_humana.xlsx           caderno para o avaliador (abas Instruções, Tópicos, Respostas)
    anotacoes/avaliacao_humana_OCULTO.csv     modelo, tópico e posição da intrusa de cada item
    data/processed/fase4/avaliacao_humana.md  resumo (acerto por modelo, coerência e, com dois avaliadores, concordância)
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from fase3_clustering import palavras_por_topico, vetorizador  # noqa: E402

P = Path("data/processed")
ANOT = Path("anotacoes")
SEED = 130
N_BERT, N_LDA, N_DOCS = 16, 8, 5
CADERNO = ANOT / "avaliacao_humana.xlsx"
OCULTO = ANOT / "avaliacao_humana_OCULTO.csv"
MODELO_PRINCIPAL = "bertimbau_nn30_mcs100_eom_ms10_rk"

INSTRUCOES = [
    "Avaliação de tópicos de proposições legislativas da Câmara dos Deputados",
    "",
    "Cada item é um grupo de proposições formado automaticamente. Na aba Tópicos, cada item traz 10 termos "
    "que descrevem o grupo e seis ementas (resumos oficiais das proposições).",
    "Cinco ementas são do grupo e uma foi colocada de propósito vinda de outro grupo (a intrusa).",
    "",
    "Na aba Respostas, para cada item:",
    "1. intrusa: o número (1 a 6) da ementa que você acha que não pertence ao grupo.",
    "2. coerencia: 3 = as ementas do grupo (sem a intrusa) tratam claramente de um mesmo assunto; "
    "2 = têm um assunto comum, com exceções ou de forma vaga; 1 = não há assunto comum reconhecível.",
    "3. rotulo (opcional): um nome curto para o assunto do grupo, se houver.",
    "",
    "Regras: responda só com base nos termos e nas ementas, sem consultar outras fontes. "
    "Não há resposta para deixar em branco: se estiver em dúvida sobre a intrusa, escolha a mais provável. "
    "Tempo estimado: 30 a 40 minutos.",
]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def gerar(a) -> None:
    ANOT.mkdir(exist_ok=True)
    if CADERNO.exists() and not a.refazer:
        raise SystemExit(f"{CADERNO} já existe. Use --refazer para sortear de novo.")
    base = pd.read_parquet(a.base, columns=["id", "ementa", "texto_modelo", "eh_formulaica"])
    t = pd.read_parquet(P / f"fase3/topicos_{MODELO_PRINCIPAL}.parquet")[["id", "topico_alt_ctfidf"]]
    lda = pd.read_parquet(P / "fase4/baselines/rotulos_baselines.parquet")[["id", "lda_k66"]]
    d = base.merge(t, on="id").merge(lda, on="id")
    d = d[~d["eh_formulaica"]].reset_index(drop=True)
    vec = vetorizador()
    X = vec.fit_transform(d["texto_modelo"].fillna("")).tocsr()
    vocab = vec.get_feature_names_out()
    rng = np.random.default_rng(SEED)
    itens = []
    for modelo, col, n in (("BERTimbau", "topico_alt_ctfidf", N_BERT), ("LDA", "lda_k66", N_LDA)):
        lab = d[col].to_numpy()
        pal = palavras_por_topico(X, lab, vocab, n=10)
        elegiveis = sorted(t_ for t_ in pal if (lab == t_).sum() >= 50)
        for top in rng.choice(elegiveis, size=n, replace=False):
            membros = d.index[lab == top].to_numpy()
            outros = d.index[lab != top].to_numpy()
            docs = list(rng.choice(membros, size=N_DOCS, replace=False))
            intrusa = int(rng.choice(outros))
            pos = int(rng.integers(0, N_DOCS + 1))
            docs.insert(pos, intrusa)
            itens.append({"modelo": modelo, "topico": int(top), "termos": ", ".join(pal[top]),
                          "docs": docs, "pos_intrusa": pos + 1})
    ordem = rng.permutation(len(itens))
    itens = [itens[i] for i in ordem]
    linhas, oculto = [], []
    for k, it in enumerate(itens, start=1):
        linhas.append({"item": k, "nº": "", "texto": "TERMOS: " + it["termos"]})
        for j, di in enumerate(it["docs"], start=1):
            linhas.append({"item": k, "nº": j, "texto": d.at[di, "ementa"]})
        linhas.append({"item": "", "nº": "", "texto": ""})
        oculto.append({"item": k, "modelo": it["modelo"], "topico": it["topico"], "intrusa_correta": it["pos_intrusa"],
                       "id_intrusa": int(d.at[it["docs"][it["pos_intrusa"] - 1], "id"])})
    resp = pd.DataFrame({"item": range(1, len(itens) + 1), "intrusa": "", "coerencia": "", "rotulo": "", "obs": ""})
    with pd.ExcelWriter(CADERNO, engine="openpyxl") as w:
        pd.DataFrame({"Instruções": INSTRUCOES}).to_excel(w, sheet_name="Instruções", index=False)
        pd.DataFrame(linhas).to_excel(w, sheet_name="Tópicos", index=False)
        resp.to_excel(w, sheet_name="Respostas", index=False)
        ws = w.sheets["Tópicos"]
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 5
        ws.column_dimensions["C"].width = 140
        w.sheets["Instruções"].column_dimensions["A"].width = 140
        w.sheets["Respostas"].column_dimensions["D"].width = 40
        w.sheets["Respostas"].column_dimensions["E"].width = 40
    pd.DataFrame(oculto).to_csv(OCULTO, index=False, encoding="utf-8-sig")
    print(f"Caderno: {CADERNO} ({len(itens)} itens: {N_BERT} BERTimbau e {N_LDA} LDA, misturados).")


def ler_respostas(caminho: Path) -> pd.DataFrame:
    r = pd.read_excel(caminho, sheet_name="Respostas")
    r = r[pd.to_numeric(r["item"], errors="coerce").notna()].copy()
    r["item"] = r["item"].astype(int)
    r["intrusa"] = pd.to_numeric(r["intrusa"], errors="coerce")
    r["coerencia"] = pd.to_numeric(r["coerencia"], errors="coerce")
    r["avaliador"] = caminho.stem.replace("avaliacao_humana_RESPOSTAS_", "")
    return r


def kappa(a: pd.Series, b: pd.Series) -> float:
    cats = sorted(set(a) | set(b))
    po = float((a.to_numpy() == b.to_numpy()).mean())
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def resumir(a) -> None:
    o = pd.read_csv(OCULTO, encoding="utf-8-sig")
    todas = [ler_respostas(Path(c)).merge(o, on="item") for c in a.respostas]
    d = pd.concat(todas, ignore_index=True)
    d["acertou"] = d["intrusa"] == d["intrusa_correta"]
    rel = ["# Avaliação humana: intrusão de ementas e coerência\n",
           f"Avaliadores: {', '.join(sorted(d['avaliador'].unique()))}. Acerto ao acaso: 1/6 (17%).\n",
           "| Avaliador | Modelo | Itens | Acerto da intrusa (IC 95%) | Coerência média | Coerência 3 |",
           "|---|---|---|---|---|---|"]
    for (av, m), x in d.groupby(["avaliador", "modelo"]):
        x = x.dropna(subset=["intrusa"])
        k, n = int(x["acertou"].sum()), len(x)
        lo, hi = wilson(k, n)
        rel.append(f"| {av} | {m} | {n} | {k}/{n} = {k / n:.0%} ({lo:.0%} a {hi:.0%}) | "
                   f"{x['coerencia'].mean():.2f} | {(x['coerencia'] == 3).mean():.0%} |")
    for m, x in d.groupby("modelo"):
        x = x.dropna(subset=["intrusa"])
        k, n = int(x["acertou"].sum()), len(x)
        lo, hi = wilson(k, n)
        rel.append(f"| todos | {m} | {n} | {k}/{n} = {k / n:.0%} ({lo:.0%} a {hi:.0%}) | "
                   f"{x['coerencia'].mean():.2f} | {(x['coerencia'] == 3).mean():.0%} |")
    avs = sorted(d["avaliador"].unique())
    if len(avs) >= 2:
        a1 = d[d["avaliador"] == avs[0]].set_index("item")
        a2 = d[d["avaliador"] == avs[1]].set_index("item")
        comuns = a1.index.intersection(a2.index)
        rel += ["", f"Concordância entre {avs[0]} e {avs[1]} ({len(comuns)} itens): "
                    f"intrusa igual em {(a1.loc[comuns, 'intrusa'] == a2.loc[comuns, 'intrusa']).mean():.0%}; "
                    f"kappa de Cohen da coerência = {kappa(a1.loc[comuns, 'coerencia'], a2.loc[comuns, 'coerencia']):.2f}."]
    (P / "fase4" / "avaliacao_humana.md").write_text("\n".join(rel), encoding="utf-8")
    print("\n".join(rel))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("--base", type=Path, default=sorted(P.glob("base_fase2_*.parquet"))[-1])
    g.add_argument("--refazer", action="store_true")
    r = sub.add_parser("resumir")
    r.add_argument("respostas", nargs="+")
    a = ap.parse_args()
    gerar(a) if a.cmd == "gerar" else resumir(a)


if __name__ == "__main__":
    main()
