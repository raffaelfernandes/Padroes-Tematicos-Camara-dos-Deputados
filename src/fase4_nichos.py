"""
fase4_nichos.py

O que há dentro dos outliers? Agrupa de novo só as proposições que o HDBSCAN deixou fora do
núcleo (UMAP e HDBSCAN ajustados só nelas) e compara o resultado com a classificação do CEDI.

Sem os núcleos grandes, regiões menores e menos densas aparecem como grupos ("nichos"): agendas
com dezenas a poucas centenas de proposições, abaixo do tamanho mínimo de 100 do modelo principal.
O que continua sem grupo é a parte dos outliers que não tem com quem se agrupar.

Perguntas respondidas no relatório:
  1. Quantos nichos aparecem e quanto fica sem grupo, para alguns tamanhos mínimos de grupo.
  2. O que são os nichos: termos (c-TF-IDF), tamanho, tópico principal mais parecido e quanto
     a reatribuição espalhou cada nicho entre tópicos diferentes.
  3. O CEDI também agrupa os nichos? Pureza de cada nicho pelo codTema (fração com o tema oficial
     mais comum), comparada com os tópicos principais e com grupos aleatórios dos mesmos tamanhos;
     precisão do BCubed nas mesmas proposições, para os nichos e para os tópicos da reatribuição.
  4. Como o CEDI classificou o que ficou sem grupo: número de temas e temas sobre-representados.

Uso (a partir de code/):
    uv run python src/fase4_nichos.py --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet

Saídas em data/processed/fase4/: nichos_<tag>.md, nichos_<tag>.csv (um nicho por linha) e
nichos_rotulos_<tag>.parquet (proposição -> nicho, -1 = sem grupo).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fase3_clustering import palavras_por_topico, vetorizador  # noqa: E402
from fase4_avaliacao import Gabarito, md, n_para_cobrir  # noqa: E402

SEED = 42           # mesma semente do UMAP da Fase 3
SEED_ALEAT = 130
SAIDA = Path("data/processed/fase4")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--temas", required=True, type=Path)
    ap.add_argument("--topicos", required=True, type=Path)
    ap.add_argument("--nn", type=int, default=15, help="vizinhos do UMAP ajustado só nos outliers")
    ap.add_argument("--mcs", type=int, default=30, help="tamanho mínimo de grupo da versão analisada")
    ap.add_argument("--min-samples", type=int, default=10)
    ap.add_argument("--mcs-sensibilidade", type=int, nargs="+", default=[15, 30, 50, 100])
    a = ap.parse_args()
    from sklearn.cluster import HDBSCAN
    from umap import UMAP

    tag = a.topicos.stem.replace("topicos_", "")
    modelo = tag.split("_")[0]
    emb = np.load(Path("data/processed/embeddings") / f"emb_{modelo}.npy")
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    u = pd.read_parquet(Path("data/processed/embeddings") / "textos_unicos.parquet").set_index("id_texto_unico")
    t = pd.read_parquet(a.topicos)
    temas = pd.read_parquet(a.temas)
    nome = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    info = pd.read_csv(a.topicos.parent / f"topic_info_{tag}.csv").set_index("Topic")
    nome_top = {int(k): "_".join(str(v).split("_")[1:4]) for k, v in info["Name"].items()}

    # ---------- textos únicos fora do núcleo (outliers reatribuídos)
    g = t.groupby("id_texto_unico").agg(origem=("origem_topico", "first"), hdb=("topico_hdbscan", "first"))
    out_u = g.index[g["origem"] == "reduce_outliers"].to_numpy()
    nuc_u = g.index[g["origem"] == "hdbscan"].to_numpy()
    E_out, E_nuc = emb[out_u], emb[nuc_u]
    y_nuc = g.loc[nuc_u, "hdb"].to_numpy()
    print(f"{len(out_u)} textos únicos fora do núcleo; {len(nuc_u)} no núcleo")

    red = UMAP(n_neighbors=a.nn, n_components=5, min_dist=0.0, metric="cosine",
               random_state=SEED, low_memory=True).fit_transform(E_out)
    sens, rotulos = [], {}
    for mcs in sorted(set(a.mcs_sensibilidade) | {a.mcs}):
        lab = HDBSCAN(min_cluster_size=mcs, min_samples=a.min_samples, cluster_selection_method="eom").fit_predict(red)
        rotulos[mcs] = lab
        tam = np.bincount(lab[lab >= 0]) if (lab >= 0).any() else np.array([0])
        sens.append({"tamanho mínimo": mcs, "nichos": int(lab.max() + 1), "sem grupo": f"{(lab == -1).mean():.1%}",
                     "maior nicho (textos)": int(tam.max()), "mediana (textos)": int(np.median(tam))})
        print(f"  mcs={mcs}: {lab.max() + 1} nichos, {(lab == -1).mean():.1%} sem grupo")
    sens = pd.DataFrame(sens)
    lab_u = pd.Series(rotulos[a.mcs], index=out_u)

    # ---------- proposições: nicho, tópico recebido na reatribuição e temas
    p = t[t["origem_topico"] == "reduce_outliers"][["id", "id_texto_unico", "topico_alt_ctfidf"]].copy()
    p["nicho"] = p["id_texto_unico"].map(lab_u).astype(int)
    p["temas"] = p["id"].map(conj)
    p = p[p["temas"].notna()].reset_index(drop=True)
    p.drop(columns="temas").to_parquet(SAIDA / f"nichos_rotulos_{tag}.parquet", index=False)

    # ---------- descrição dos nichos
    cent = np.vstack([E_nuc[y_nuc == k].mean(0) for k in range(int(y_nuc.max()) + 1)])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    lab = rotulos[a.mcs]
    textos = u.loc[out_u, "texto_modelo"].fillna("").to_numpy()
    cv = vetorizador("docs")
    X = cv.fit_transform(textos)
    pal = palavras_por_topico(X, lab, np.array(cv.get_feature_names_out()), n=6)
    linhas = []
    for k in range(int(lab.max()) + 1):
        m = lab == k
        ce = E_out[m].mean(0)
        ce /= np.linalg.norm(ce)
        s = cent @ ce
        pk = p[p["nicho"] == k]
        cont = pd.Series([c for st in pk["temas"] for c in st]).value_counts()
        dom = cont.index[0] if len(cont) else None
        linhas.append({
            "nicho": k, "termos": ", ".join(pal.get(k, [])[:5]), "proposicoes": len(pk),
            "topico_mais_parecido": f"{int(s.argmax())} ({nome_top.get(int(s.argmax()), '')})",
            "similaridade": round(float(s.max()), 3),
            "no_mesmo_topico_reatrib": round(float(pk["topico_alt_ctfidf"].value_counts(normalize=True).iloc[0]), 2) if len(pk) else np.nan,
            "tema_cedi_dominante": nome.get(dom, ""),
            "pureza_cedi": round(float(pk["temas"].map(lambda st: dom in st).mean()), 3) if len(pk) else np.nan,
            "temas_para_80pct": n_para_cobrir(cont) if len(cont) else np.nan,
        })
    nichos = pd.DataFrame(linhas).sort_values("proposicoes", ascending=False)
    nichos.to_csv(SAIDA / f"nichos_{tag}.csv", index=False)

    # ---------- o CEDI também agrupa os nichos?
    rng = np.random.default_rng(SEED_ALEAT)

    def pureza(rot: np.ndarray, temas_: pd.Series) -> np.ndarray:
        res = []
        for k in np.unique(rot[rot >= 0]):
            ts = temas_[rot == k]
            cont = pd.Series([c for st in ts for c in st]).value_counts()
            res.append(ts.map(lambda st: cont.index[0] in st).mean())
        return np.array(res)

    agr = p[p["nicho"] >= 0].reset_index(drop=True)
    rot_n = agr["nicho"].to_numpy()
    pur_nichos = pureza(rot_n, agr["temas"])
    pur_aleat = np.median([np.median(pureza(rng.permutation(rot_n), agr["temas"])) for _ in range(5)])
    todos = t[["id", "topico_alt_ctfidf"]].assign(temas=lambda x: x["id"].map(conj)).dropna(subset=["temas"]).reset_index(drop=True)
    pur_topicos = pureza(todos["topico_alt_ctfidf"].to_numpy(), todos["temas"])

    gab = Gabarito(list(agr["temas"]))
    P_n, _ = gab.por_item(rot_n)
    P_r, _ = gab.por_item(agr["topico_alt_ctfidf"].to_numpy())
    P_a = np.mean([gab.por_item(rng.permutation(rot_n))[0].mean() for _ in range(5)])
    concord = pd.DataFrame([
        {"comparação": "pureza mediana pelo CEDI: nichos", "valor": round(float(np.median(pur_nichos)), 3)},
        {"comparação": "pureza mediana pelo CEDI: grupos aleatórios dos mesmos tamanhos", "valor": round(float(pur_aleat), 3)},
        {"comparação": "pureza mediana pelo CEDI: 66 tópicos principais", "valor": round(float(np.median(pur_topicos)), 3)},
        {"comparação": "precisão BCubed (só proposições em nichos): agrupadas pelos nichos", "valor": round(float(P_n.mean()), 3)},
        {"comparação": "precisão BCubed (mesmas proposições): agrupadas pelos tópicos da reatribuição", "valor": round(float(P_r.mean()), 3)},
        {"comparação": "precisão BCubed (mesmas proposições): nichos embaralhados", "valor": round(float(P_a), 3)},
    ])

    # ---------- como o CEDI classificou o que ficou sem grupo
    nuc_p = t[t["origem_topico"] == "hdbscan"][["id"]].assign(temas=lambda x: x["id"].map(conj)).dropna()
    grupos = {"núcleo do HDBSCAN": nuc_p["temas"], "outliers em nichos": agr["temas"],
              "outliers sem grupo": p.loc[p["nicho"] == -1, "temas"]}
    perfil = pd.DataFrame([{"grupo": k, "proposicoes": len(v), "temas por proposição": round(v.map(len).mean(), 2),
                            "com 4 ou mais temas": f"{(v.map(len) >= 4).mean():.1%}"} for k, v in grupos.items()])
    ref = pd.Series([c for st in todos["temas"] for c in st]).value_counts(normalize=True)
    sg = pd.Series([c for st in grupos["outliers sem grupo"] for c in st]).value_counts(normalize=True)
    lift = (sg / ref).dropna().rename("razão").to_frame()
    lift["tema"] = [nome[c] for c in lift.index]
    lift["% das classificações (sem grupo)"] = (100 * sg.reindex(lift.index)).round(1)
    lift["% das classificações (corpus)"] = (100 * ref.reindex(lift.index)).round(1)
    lift["razão"] = lift["razão"].round(2)
    lift = lift[ref.reindex(lift.index) >= 0.005].sort_values("razão", ascending=False)
    cols = ["tema", "% das classificações (sem grupo)", "% das classificações (corpus)", "razão"]

    n_em_nicho = int((p["nicho"] >= 0).sum())
    rel = [f"# Nichos dentro dos outliers: {tag}\n",
           f"UMAP ({a.nn} vizinhos, 5 dimensões, semente {SEED}) e HDBSCAN (eom, min_samples {a.min_samples}) ajustados só nos "
           f"{len(out_u)} textos únicos fora do núcleo. Versão analisada: tamanho mínimo {a.mcs}.\n",
           "## Sensibilidade ao tamanho mínimo de grupo\n", md(sens), "",
           f"Na versão analisada: {int(lab.max() + 1)} nichos com {n_em_nicho} proposições "
           f"({n_em_nicho / len(p):.1%} dos outliers com tema oficial); {int((p['nicho'] == -1).sum())} proposições sem grupo. "
           f"Em média, {nichos['no_mesmo_topico_reatrib'].mean():.0%} das proposições de um nicho foram reatribuídas ao mesmo tópico.\n",
           "## Os 30 maiores nichos\n", md(nichos.head(30)), "",
           "## O CEDI também agrupa os nichos?\n", md(concord), "",
           "## Como o CEDI classificou cada grupo\n", md(perfil), "",
           "### Temas mais sobre-representados no que ficou sem grupo (razão sobre o corpus)\n", md(lift[cols].head(10)), "",
           "### Temas mais sub-representados no que ficou sem grupo\n", md(lift[cols].tail(6)), ""]
    (SAIDA / f"nichos_{tag}.md").write_text("\n".join(rel), encoding="utf-8")
    print(concord.to_string(index=False)); print(perfil.to_string(index=False))
    print(f"Relatório: {SAIDA / f'nichos_{tag}.md'}")


if __name__ == "__main__":
    main()
