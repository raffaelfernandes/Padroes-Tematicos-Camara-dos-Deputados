"""
baselines_classicos.py

Extra da revisão final do TCC (14/11/2026). Responde à pergunta "os embeddings ajudaram?",
comparando o modelo principal com três baselines que não usam modelos de linguagem:

  lda        LDA (sklearn) com k tópicos sobre contagens de palavras; cada texto vai para o tópico
             de maior peso.
  kmeans     TF-IDF + K-Means com k grupos.
  tfidf_bt   o mesmo pipeline do modelo principal (UMAP com 30 vizinhos e 5 dimensões, HDBSCAN com
             tamanho mínimo 100, min_samples 10 e eom, outliers reatribuídos pelo voto dos 15 vizinhos
             do núcleo), só trocando os embeddings por TF-IDF reduzido a 300 dimensões (SVD).
             Isola o efeito dos embeddings dentro do mesmo pipeline.

Mesmo protocolo do modelo principal: ajuste só nos textos únicos das ementas substantivas, formulaicas
atribuídas depois pelo próprio modelo (transform/predict, ou vizinhos no caso do tfidf_bt), mesmo
vetorizador do c-TF-IDF, semente SEED_BASELINES (42, de src/seed.py). Avaliação: BCubed estendido contra o codTema, pares de
apensada e principal no mesmo grupo, NPMI das 10 palavras de c-TF-IDF e diversidade (mesmas funções
da Fase 3), tamanho do maior grupo. Os tópicos dos três modelos neurais entram na mesma tabela,
medidos pelas mesmas funções.

Uso (a partir de code/):
    uv run python src/extras/baselines_classicos.py
    uv run python src/extras/baselines_classicos.py --k 66 32 --so lda kmeans
    uv run python src/extras/baselines_classicos.py --so nenhum     (só reavalia os modelos neurais)

Saídas em data/processed/fase4/baselines/ (resultados.csv, relatorio.md e os rótulos de cada baseline).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

sys.path.insert(0, "src")
from fase3_clustering import STOP_PT, diversidade, npmi_medio, palavras_por_topico, vetorizador  # noqa: E402
from fase4_avaliacao import Gabarito  # noqa: E402

P = Path("data/processed")
SAIDA = P / "fase4" / "baselines"
from seed import SEED as SEED_ACASO, SEED_BASELINES as SEED  # noqa: E402  (ver src/seed.py)
NEURAIS = {
    "BERTimbau Large (modelo principal)": "bertimbau_nn30_mcs100_eom_ms10_rk",
    "Serafim 335M": "serafim_nn30_mcs100_eom_ms5_rk",
    "multilingual-e5-large": "e5_nn30_mcs100_eom_ms10_rk",
}


def md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) if len(df) else "(vazio)"


def reatribui_knn(Z: np.ndarray, lab: np.ndarray, k: int = 15) -> np.ndarray:
    """Outliers (-1) recebem o tópico mais votado entre os k vizinhos do núcleo, com peso pela similaridade."""
    nuc = np.nonzero(lab != -1)[0]
    out = np.nonzero(lab == -1)[0]
    lab = lab.copy()
    if len(out) == 0:
        return lab
    nn = NearestNeighbors(n_neighbors=k, metric="cosine").fit(Z[nuc])
    dist, ind = nn.kneighbors(Z[out])
    sim = 1 - dist
    viz = lab[nuc][ind]
    for i, o in enumerate(out):
        votos = pd.Series(sim[i]).groupby(viz[i]).sum()
        lab[o] = int(votos.idxmax())
    return lab


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=sorted(P.glob("base_fase2_*.parquet"))[-1])
    ap.add_argument("--temas", type=Path, default=P / "temas_long_20261027.parquet")
    ap.add_argument("--k", type=int, nargs="+", default=[66, 32])
    ap.add_argument("--so", nargs="+", default=["lda", "kmeans", "tfidf_bt"], choices=["lda", "kmeans", "tfidf_bt", "nenhum"],
                    help='"nenhum": só reavalia os modelos neurais e mantém as linhas dos baselines do resultados.csv anterior')
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)

    base = pd.read_parquet(a.base, columns=["id", "id_texto_unico", "texto_modelo", "eh_formulaica", "idPropPrincipal"])
    u = base.drop_duplicates("id_texto_unico").sort_values("id_texto_unico").reset_index(drop=True)
    form_u = base.groupby("id_texto_unico")["eh_formulaica"].all().reindex(u["id_texto_unico"]).to_numpy()
    pos = pd.Series(np.arange(len(u)), index=u["id_texto_unico"])
    mapa = pos.loc[base["id_texto_unico"]].to_numpy()          # proposição -> texto único
    docs = u["texto_modelo"].fillna("").tolist()
    fit = np.nonzero(~form_u)[0]
    print(f"{len(base)} proposições, {len(u)} textos únicos, {len(fit)} substantivos para ajuste")

    # vetorizador da Fase 3 (o mesmo do c-TF-IDF e do NPMI), ajustado nas substantivas
    vec = vetorizador()
    X_fit = vec.fit_transform([docs[i] for i in fit]).tocsr()
    X_all = vec.transform(docs).tocsr()
    vocab = vec.get_feature_names_out()
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    Xb_fit = (X_fit > 0).astype(np.float32).tocsc()

    # gabarito e apensadas
    temas = pd.read_parquet(a.temas)
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    tem = base["id"].map(conj)
    ok = tem.notna().to_numpy()
    gab = Gabarito(list(tem[ok]))
    ids = base["id"].to_numpy()
    pos_id = pd.Series(np.arange(len(base)), index=ids)
    pr = base.dropna(subset=["idPropPrincipal"])
    pr = pr[pr["idPropPrincipal"].astype("int64").isin(ids)]
    ia = pos_id.loc[pr["id"]].to_numpy()
    ib = pos_id.loc[pr["idPropPrincipal"].astype("int64")].to_numpy()

    def avalia(nome: str, k_alvo, lab_u: np.ndarray, extra: dict | None = None) -> dict:
        """lab_u: um grupo por texto único (sem -1)."""
        lab_p = lab_u[mapa]
        r = gab.bcubed(lab_p[ok])
        pal = palavras_por_topico(X_fit, lab_u[fit], vocab)
        tam = pd.Series(lab_p).value_counts(normalize=True)
        # acaso com os mesmos tamanhos de grupo (5 sementes): separa o ganho real do efeito do tamanho dos grupos
        rng = np.random.default_rng(SEED_ACASO)
        ale = [gab.bcubed(rng.permutation(lab_p[ok])) for _ in range(5)]
        p_ale = float(np.mean([x["P"] for x in ale])); r_ale = float(np.mean([x["R"] for x in ale]))
        ap_ale = float(np.mean([(lambda q: (q[ia] == q[ib]).mean())(rng.permutation(lab_p)) for _ in range(5)]))
        ap = float((lab_p[ia] == lab_p[ib]).mean())
        linha = {"modelo": nome, "k_pedido": k_alvo, "grupos": int(pd.Series(lab_p).nunique()),
                 "P": round(r["P"], 3), "R": round(r["R"], 3), "F": round(r["F"], 3),
                 "P_acaso": round(p_ale, 3), "R_acaso": round(r_ale, 3),
                 "P_sobre_acaso": round(r["P"] / p_ale, 2), "R_sobre_acaso": round(r["R"] / r_ale, 2),
                 "apensadas_mesmo_grupo": round(ap, 3), "apensadas_acaso": round(ap_ale, 3),
                 "npmi": round(npmi_medio(Xb_fit, pal, vocab_idx), 3),
                 "diversidade": round(diversidade(pal), 3),
                 "maior_grupo": round(float(tam.iloc[0]), 3)}
        if extra:
            linha.update(extra)
        print(linha, flush=True)
        return linha

    linhas, exemplos = [], {}

    # modelos neurais, medidos com as mesmas funções
    for nome, tag in NEURAIS.items():
        t = pd.read_parquet(P / f"fase3/topicos_{tag}.parquet")[["id", "topico_alt_ctfidf"]]
        lab_por_id = t.set_index("id")["topico_alt_ctfidf"]
        lab_u = np.full(len(u), -1)
        lab_u[mapa] = lab_por_id.reindex(base["id"]).to_numpy()
        linhas.append(avalia(nome, "natural", lab_u))

    # baselines
    for k in a.k:
        if "lda" in a.so:
            t0 = time.time()
            lda = LatentDirichletAllocation(n_components=k, learning_method="online", batch_size=2048,
                                            max_iter=20, random_state=SEED, n_jobs=-1)
            lda.fit(X_fit)
            lab_u = lda.transform(X_all).argmax(1)
            linhas.append(avalia("LDA (contagens)", k, lab_u, {"segundos": round(time.time() - t0)}))
            exemplos[f"lda_k{k}"] = lab_u
        if "kmeans" in a.so:
            t0 = time.time()
            tf = TfidfVectorizer(stop_words=list(STOP_PT), token_pattern=r"(?u)\b[^\W\d_]{3,}\b",
                                 ngram_range=(1, 2), min_df=5, max_df=0.5, sublinear_tf=True)
            T_fit = tf.fit_transform([docs[i] for i in fit])
            km = KMeans(n_clusters=k, n_init=5, random_state=SEED).fit(T_fit)
            lab_u = km.predict(tf.transform(docs))
            linhas.append(avalia("TF-IDF + K-Means", k, lab_u, {"segundos": round(time.time() - t0)}))
            exemplos[f"kmeans_k{k}"] = lab_u

    if "tfidf_bt" in a.so:
        from umap import UMAP
        t0 = time.time()
        tf = TfidfVectorizer(stop_words=list(STOP_PT), token_pattern=r"(?u)\b[^\W\d_]{3,}\b",
                             ngram_range=(1, 2), min_df=5, max_df=0.5, sublinear_tf=True)
        T_fit = tf.fit_transform([docs[i] for i in fit])
        svd = TruncatedSVD(n_components=300, random_state=SEED).fit(T_fit)
        Z_all = normalize(svd.transform(tf.transform(docs)))
        Z_fit = Z_all[fit]
        red = UMAP(n_neighbors=30, n_components=5, min_dist=0.0, metric="cosine",
                   random_state=SEED, low_memory=True).fit_transform(Z_fit)
        lab_fit = HDBSCAN(min_cluster_size=100, min_samples=10, cluster_selection_method="eom").fit(red).labels_
        pct_out = float((lab_fit == -1).mean())
        n_top = int(len(set(lab_fit)) - (1 if -1 in lab_fit else 0))
        lab_fit_r = reatribui_knn(Z_fit, lab_fit)
        # formulaicas: voto dos 15 vizinhos entre as substantivas já rotuladas
        lab_u = np.full(len(u), -1)
        lab_u[fit] = lab_fit_r
        form = np.nonzero(form_u)[0]
        if len(form):
            nn = NearestNeighbors(n_neighbors=15, metric="cosine").fit(Z_fit)
            dist, ind = nn.kneighbors(Z_all[form])
            for i, f in enumerate(form):
                lab_u[f] = int(pd.Series(1 - dist[i]).groupby(lab_fit_r[ind[i]]).sum().idxmax())
        linhas.append(avalia("TF-IDF no pipeline do BERTopic (UMAP + HDBSCAN)", "natural", lab_u,
                             {"pct_outliers": round(pct_out, 3), "topicos_hdbscan": n_top,
                              "segundos": round(time.time() - t0)}))
        exemplos["tfidf_bt"] = lab_u

    res = pd.DataFrame(linhas)
    anterior = SAIDA / "resultados.csv"
    if anterior.exists():   # mantém as linhas dos baselines que não foram reajustados nesta execução
        velho = pd.read_csv(anterior)
        refeitos = set(res["modelo"] + "|" + res["k_pedido"].astype(str))
        velho = velho[~(velho["modelo"] + "|" + velho["k_pedido"].astype(str)).isin(refeitos)
                      & ~velho["modelo"].isin(list(NEURAIS))]
        res = pd.concat([res, velho], ignore_index=True)
    res.to_csv(anterior, index=False)
    if exemplos:            # só regrava os rótulos se algum baseline foi reajustado
        rot_p = SAIDA / "rotulos_baselines.parquet"
        rot = pd.read_parquet(rot_p) if rot_p.exists() else pd.DataFrame({"id": base["id"]})
        for k, v in exemplos.items():
            rot = rot.drop(columns=[k], errors="ignore").merge(pd.DataFrame({"id": base["id"], k: v[mapa]}), on="id", how="right")
        rot.to_parquet(rot_p, index=False)
    rel = ["# Baselines clássicos contra os modelos neurais\n",
           f"Base: `{a.base.name}`. Ajuste nas {len(fit)} ementas substantivas únicas; semente dos baselines {SEED} "
           f"(ajustados em 14/11/2026 sobre o texto_modelo, que não muda com o texto do embedding). "
           "NPMI e diversidade calculados com as funções da Fase 3 sobre as palavras de c-TF-IDF de cada grupo "
           "(todos os grupos, depois da reatribuição), então o NPMI dos modelos neurais aqui difere um pouco do "
           "da grade, que olhava só o núcleo do HDBSCAN.\n", md(res)]
    (SAIDA / "relatorio.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {SAIDA / 'relatorio.md'}")


if __name__ == "__main__":
    main()
