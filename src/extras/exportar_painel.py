"""
exportar_painel.py

Gera data/processed/fase4/painel_dados.json com os agregados usados no painel visual
dos resultados (tópicos, temas, BCubed, mapa 2D). Rodar a partir de code/:
    uv run python src/extras/exportar_painel.py
"""
import glob, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from fase4_avaliacao import Gabarito, entropia_norm, n_para_cobrir

P = Path("data/processed")
MODELO = "bertimbau_nn30_mcs100_eom_ms10"
COL = "topico_alt_ctfidf"          # versão principal: formulaicas pelo c-TF-IDF

base = pd.read_parquet(sorted(P.glob("base_fase2_*.parquet"))[-1],
                       columns=["id", "id_texto_unico", "siglaTipo", "ementa", "eh_formulaica", "idPropPrincipal"])
temas = pd.read_parquet(P / "temas_long_20261027.parquet")
nome_tema = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
t = pd.read_parquet(P / f"fase3/topicos_{MODELO}.parquet")
info = pd.read_csv(P / f"fase3/topic_info_{MODELO}.csv")
termos = info.set_index("Topic")["Representation"].map(lambda s: [w.strip(" '\"") for w in s.strip("[]").split(",")])

d = base.merge(t.drop(columns=["id_texto_unico"]), on="id")
d["temas"] = d["id"].map(conj)
dt = d[d["temas"].notna()].reset_index(drop=True)
g = Gabarito(list(dt["temas"]))
Pi, Ri = g.por_item(dt[COL].to_numpy())
dt["P"], dt["R"] = Pi, Ri
dt["P_acaso"] = g.denom[g.sig] / len(dt)

# Tópicos
topicos = []
for tp, x in dt.groupby(COL):
    cont = pd.Series([c for s in x["temas"] for c in s]).value_counts()
    nuc = x[x["origem_topico"] == "hdbscan"]
    topicos.append({
        "id": int(tp), "termos": termos.get(tp, [])[:6], "n": int((d[COL] == tp).sum()),
        "n_nucleo": int((d.loc[d[COL] == tp, "origem_topico"] == "hdbscan").sum()),
        "n_reatrib": int((d.loc[d[COL] == tp, "origem_topico"] == "reduce_outliers").sum()),
        "n_form": int((d.loc[d[COL] == tp, "origem_topico"] == "formulaica_centroide").sum()),
        "pureza": round(float(x["temas"].map(lambda s: cont.index[0] in s).mean()), 3),
        "tema_dom": nome_tema[cont.index[0]],
        "temas_top": [[nome_tema[c], round(v / len(x), 3)] for c, v in cont.head(4).items()],
        "temas80": n_para_cobrir(cont),
        "P": round(float(x["P"].mean()), 3), "R": round(float(x["R"].mean()), 3),
        "P_nucleo": round(float(nuc["P"].mean()), 3) if len(nuc) else None,
        "disp": int((x["P"] < x["P_acaso"]).sum()),
        "exemplos": nuc["ementa"].drop_duplicates().sample(min(3, nuc["ementa"].nunique()), random_state=1).str.slice(0, 160).tolist() if len(nuc) else [],
    })

# Temas (fragmentação)
longo = dt[["id", COL, "temas"]].explode("temas").reset_index(drop=True)
temas_out = []
for c, x in longo.groupby("temas"):
    cont = x[COL].value_counts()
    temas_out.append({"tema": nome_tema[int(c)], "n": int(cont.sum()), "n_topicos": int(cont.size),
                      "topicos80": n_para_cobrir(cont), "entropia": round(entropia_norm(cont.to_numpy()), 3),
                      "maior_pct": round(float(cont.iloc[0] / cont.sum()), 3),
                      "top": [[int(i), round(float(v / cont.sum()), 3)] for i, v in cont.head(5).items()]})

# Matriz tópico x tema (fração das proposições do tópico com o tema)
ordem_temas = [x["tema"] for x in sorted(temas_out, key=lambda z: -z["n"])]
cod = {v: k for k, v in nome_tema.items()}
matriz = {str(tp): [round(float(x["temas"].map(lambda s: cod[tn] in s).mean()), 3) for tn in ordem_temas]
          for tp, x in dt.groupby(COL)}

# Mapa 2D: PCA do UMAP de 5 dimensões usado no ajuste
u = pd.read_parquet(P / "embeddings/textos_unicos.parquet")
form_u = d.groupby("id_texto_unico")["eh_formulaica"].all().reindex(u["id_texto_unico"]).to_numpy()
idx_fit = np.nonzero(~form_u)[0]
red = np.load(max(glob.glob(str(P / "fase3/umap_bertimbau_nn30_*.npy")), key=os.path.getmtime))
assert len(red) == len(idx_fit), "cache do UMAP não corresponde à base"
Xc = red - red.mean(0)
_, _, Vt = np.linalg.svd(Xc[::7], full_matrices=False)
xy = Xc @ Vt[:2].T
por_texto = d.drop_duplicates("id_texto_unico").set_index("id_texto_unico")
top_fit = por_texto.loc[u["id_texto_unico"].to_numpy()[idx_fit], COL].to_numpy()
ori_fit = por_texto.loc[u["id_texto_unico"].to_numpy()[idx_fit], "origem_topico"].to_numpy()
rng = np.random.default_rng(7)
amostra = rng.choice(len(idx_fit), 3500, replace=False)
pontos = [[round(float(xy[i, 0]), 3), round(float(xy[i, 1]), 3), int(top_fit[i]), 1 if ori_fit[i] == "hdbscan" else 0] for i in amostra]
centros = {str(tp): [round(float(v), 3) for v in xy[(top_fit == tp) & (ori_fit == "hdbscan")].mean(0)]
           for tp in np.unique(top_fit) if ((top_fit == tp) & (ori_fit == "hdbscan")).any()}

# Origem, tipo e apensadas
origem = dt.groupby("origem_topico").agg(n=("P", "size"), P=("P", "mean"), R=("R", "mean")).round(3).reset_index().to_dict("records")
tipo = dt.groupby("siglaTipo").agg(n=("P", "size"), P=("P", "mean"), R=("R", "mean")).round(3).reset_index().to_dict("records")
topo = d.set_index("id")
pares = d[d["idPropPrincipal"].notna() & d["idPropPrincipal"].isin(topo.index)]
mesmo = float((topo.loc[pares["id"], COL].to_numpy() == topo.loc[pares["idPropPrincipal"].astype(int), COL].to_numpy()).mean())
acaso = float((d[COL].value_counts(normalize=True) ** 2).sum())

bc = pd.read_csv(P / "fase4/bcubed_resultados.csv").to_dict("records")
pt = pd.read_csv(P / "fase4/bcubed_por_tipo.csv").to_dict("records")
out = {"modelo": MODELO, "n_corpus": int(len(d)), "n_com_tema": int(len(dt)), "n_formulaicas": int(d["eh_formulaica"].sum()),
       "n_topicos": len(topicos), "origem_contagem": d["origem_topico"].value_counts().to_dict(),
       "topicos": topicos, "temas": temas_out, "ordem_temas": ordem_temas, "matriz": matriz,
       "pontos": pontos, "centros": centros, "origem": origem, "tipo": tipo,
       "apensadas": {"pares": int(len(pares)), "mesmo_topico": round(mesmo, 4), "acaso": round(acaso, 4)},
       "dispersao": {"n": int((dt["P"] < dt["P_acaso"]).sum()), "pct": round(float((dt["P"] < dt["P_acaso"]).mean()), 4)},
       "bcubed": bc, "por_tipo": pt}
(P / "fase4/painel_dados.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("ok", len(json.dumps(out)) // 1024, "KB")
