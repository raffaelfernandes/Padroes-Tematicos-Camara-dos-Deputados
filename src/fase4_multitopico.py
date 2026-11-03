"""
fase4_multitopico.py

Teste de robustez: o que muda se uma proposição puder pertencer a mais de um tópico?

O gabarito (codTema) é multirrótulo (2,14 temas por proposição) e o modelo atribui um tópico
por proposição. Este script deixa cada proposição ganhar tópicos extras quando eles recebem
uma fração suficiente dos votos dos k vizinhos mais próximos do núcleo do HDBSCAN (espaço
original dos embeddings, peso = similaridade), e mede tudo de novo com o BCubed estendido
para agrupamentos com sobreposição (Amigó et al., 2009):

    precisão(e, e') = min(|C(e) ∩ C(e')|, |L(e) ∩ L(e')|) / |C(e) ∩ C(e')|
    recall(e, e')   = min(|C(e) ∩ C(e')|, |L(e) ∩ L(e')|) / |L(e) ∩ L(e')|

em que C são os tópicos e L os temas oficiais. P(e) é a média sobre os e' que dividem algum
tópico com e; R(e), sobre os que dividem algum tema. Para caber na memória, a média é
estimada numa amostra de proposições (semente 130), comparadas com o corpus inteiro.
Referência aleatória: os mesmos conjuntos de tópicos, embaralhados entre as proposições.

Também mede se ter vários temas oficiais deixa o texto mais ambíguo e quais temas quase
nunca aparecem sozinhos (indexação transversal).

Uso (a partir de code/):
    uv run python src/fase4_multitopico.py --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet

Saídas em data/processed/fase4/: multitopico_<tag>.md e multitopico_<tag>.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 130
COL = "topico_alt_ctfidf"
LIMIARES = [(None, "1 tópico (versão atual)"), (0.5, "≥ 50% dos votos"), (0.34, "≥ 34% dos votos"),
            (0.25, "≥ 25% dos votos"), (0.15, "≥ 15% dos votos")]
SAIDA = Path("data/processed/fase4")


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lin = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    lin += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lin)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--temas", required=True, type=Path)
    ap.add_argument("--topicos", required=True, type=Path)
    ap.add_argument("--k", type=int, default=15)
    ap.add_argument("--amostra", type=int, default=4000)
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    tag = a.topicos.stem.replace("topicos_", "")

    b = pd.read_parquet(a.base, columns=["id", "id_texto_unico"])
    t = pd.read_parquet(a.topicos).drop(columns="id_texto_unico")
    temas = pd.read_parquet(a.temas)
    nome = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: sorted(int(x) for x in s))
    d = b.merge(t, on="id", validate="one_to_one")
    d = d[d["id"].isin(conj.index)].reset_index(drop=True)
    cods = sorted(nome)
    ci = {c: i for i, c in enumerate(cods)}
    L = np.zeros((len(d), len(cods)), np.float32)
    for i, s in enumerate(d["id"].map(conj)):
        L[i, [ci[c] for c in s]] = 1
    own = d[COL].to_numpy()
    T = int(own.max()) + 1

    modelo = tag.split("_")[0]
    emb = np.load(Path("data/processed/embeddings") / f"emb_{modelo}.npy", mmap_mode="r")
    E = np.asarray(emb[d["id_texto_unico"].to_numpy()], np.float32)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    nuc = np.nonzero(d["origem_topico"].to_numpy() == "hdbscan")[0]
    pos_nuc = np.full(len(d), -1)
    pos_nuc[nuc] = np.arange(len(nuc))
    Ec, yc = E[nuc], own[nuc]

    # Fração (ponderada) dos votos dos k vizinhos do núcleo em cada tópico; o item não vota em si mesmo
    share = np.zeros((len(d), T), np.float32)
    for s0 in range(0, len(d), 1000):
        idx = np.arange(s0, min(s0 + 1000, len(d)))
        S = E[idx] @ Ec.T
        proprio = pos_nuc[idx] >= 0
        S[np.nonzero(proprio)[0], pos_nuc[idx][proprio]] = -1
        nb = np.argpartition(-S, a.k, axis=1)[:, :a.k]
        w = np.take_along_axis(S, nb, 1)
        M = np.zeros((len(idx), T), np.float32)
        np.add.at(M, (np.repeat(np.arange(len(idx)), a.k), yc[nb].ravel()), w.ravel())
        share[idx] = M / M.sum(1, keepdims=True)

    amostra = rng.choice(len(d), min(a.amostra, len(d)), replace=False)

    def bcubed(C: np.ndarray) -> tuple[float, float]:
        P, R = [], []
        for s0 in range(0, len(amostra), 250):
            idx = amostra[s0:s0 + 250]
            Co, Lo = C[idx] @ C.T, L[idx] @ L.T
            mn = np.minimum(Co, Lo)
            with np.errstate(invalid="ignore", divide="ignore"):
                P += list(np.where(Co > 0, mn / Co, 0).sum(1) / (Co > 0).sum(1))
                R += list(np.where(Lo > 0, mn / Lo, 0).sum(1) / (Lo > 0).sum(1))
        return float(np.mean(P)), float(np.mean(R))

    linhas, conjuntos = [], {}
    for tau, rot in LIMIARES:
        C = np.zeros((len(d), T), np.float32)
        C[np.arange(len(d)), own] = 1
        if tau is not None:
            C[share >= tau] = 1
        n = C.sum(1)
        p, r = bcubed(C)
        pa, ra = bcubed(C[rng.permutation(len(d))])
        conjuntos[tau] = n
        linhas.append({"tópicos extras": rot, "tópicos por proposição": round(float(n.mean()), 2),
                       "com 2 ou mais": f"{np.mean(n > 1):.1%}", "P": round(p, 3), "R": round(r, 3),
                       "P aleatório": round(pa, 3), "R aleatório": round(ra, 3),
                       "P / aleatório": round(p / pa, 2), "R / aleatório": round(r / ra, 2)})
        print(f"{rot:<26} P={p:.3f} R={r:.3f} (aleatório {pa:.3f} / {ra:.3f}), {np.mean(n > 1):.1%} com 2+")
    tab = pd.DataFrame(linhas)
    tab.to_csv(SAIDA / f"multitopico_{tag}.csv", index=False)

    # Ambiguidade no texto por número de temas oficiais (limiar de 25%)
    d["n_temas"] = L.sum(1).astype(int)
    d["n_top"] = conjuntos[0.25]
    amb = (d.assign(faixa=d["n_temas"].clip(upper=4).map({1: "1", 2: "2", 3: "3", 4: "4 ou mais"}))
             .groupby("faixa").agg(proposicoes=("id", "size"), com_2_topicos=("n_top", lambda s: f"{(s > 1).mean():.1%}"))
             .reset_index())
    nucleo = d["origem_topico"] == "hdbscan"
    amb_nuc = (d.loc[nucleo, "n_top"] > 1).mean()
    amb_out = (d.loc[d["origem_topico"] == "reduce_outliers", "n_top"] > 1).mean()

    # Temas que quase nunca aparecem sozinhos
    sozinho = pd.DataFrame({"tema": [nome[c] for c in cods], "proposicoes": L.sum(0).astype(int),
                            "sozinho": [(L[:, j].astype(bool) & (d["n_temas"] == 1)).sum() for j in range(len(cods))]})
    sozinho = sozinho[sozinho["proposicoes"] >= 300]
    sozinho["% sozinho"] = (100 * sozinho["sozinho"] / sozinho["proposicoes"]).round(1)
    sozinho = sozinho.sort_values("% sozinho")[["tema", "proposicoes", "% sozinho"]]

    rel = [f"# Múltiplos tópicos por proposição: {tag}\n",
           f"Tópicos extras pelo voto dos {a.k} vizinhos do núcleo (espaço original). BCubed estendido com sobreposição, "
           f"estimado em {len(amostra)} proposições sorteadas (semente {SEED}) contra o corpus inteiro "
           f"({len(d)} proposições com tema oficial, {L.sum(1).mean():.2f} temas por proposição).\n",
           md(tab), "",
           "## Ambiguidade no texto por número de temas oficiais (limiar de 25%)\n", md(amb), "",
           f"Com 2 ou mais tópicos: núcleo do HDBSCAN {amb_nuc:.1%}; outliers reatribuídos {amb_out:.1%}.\n",
           "## Temas oficiais e quanto aparecem sozinhos (temas com 300 ou mais proposições)\n", md(sozinho), ""]
    anot = Path("anotacoes/outliers_analise_erros.csv")
    if anot.exists():
        an = pd.read_csv(anot, encoding="utf-8-sig")
        an["motivo"] = an["motivo"].astype(str).str.strip().str.upper().str[:1]
        an = an.merge(d[["id", "n_top"]], on="id", how="left")
        g = an.groupby("motivo")["n_top"].agg(anotados="size", com_2_topicos=lambda s: f"{(s > 1).mean():.0%}").reset_index()
        rel += ["## Outliers anotados com 2 ou mais tópicos, por motivo (limiar de 25%)\n", md(g), ""]
    (SAIDA / f"multitopico_{tag}.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {SAIDA / f'multitopico_{tag}.md'}")


if __name__ == "__main__":
    main()
