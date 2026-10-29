"""
fase3_clustering.py

Fase 3 do TCC: redução (UMAP), agrupamento (HDBSCAN) e escolha da configuração.
A escolha usa só métricas intrínsecas. O codTema NÃO é lido aqui, para que a
avaliação da Fase 4 seja honesta.

Dois comandos:

  grade   roda a grade do HDBSCAN sobre o UMAP em cache e registra cada run em runs_log.csv
          uv run python src/fase3_clustering.py grade --modelo bertimbau --base data/processed/base_fase2_AAAAMMDD.parquet

  final   ajusta o BERTopic na configuração escolhida, reduz outliers e salva tópicos e leitura qualitativa
          uv run python src/fase3_clustering.py final --modelo bertimbau --base ... --nn 15 --mcs 50 --metodo leaf

Entradas: data/processed/embeddings/textos_unicos.parquet e emb_<modelo>.npy (do src/fase3_embeddings.py)
Saídas:   data/processed/fase3/
"""

from __future__ import annotations

import argparse
import json
import time
from itertools import combinations, product
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

SEED = 42

STOP_PT = set("""a à às ao aos aquela aquelas aquele aqueles aquilo as até com como da das de dela delas dele
deles depois do dos e é ela elas ele eles em entre era essa essas esse esses esta está estas este estes
eu foi for foram há isso isto já lhe lhes mais mas me mesmo meu minha muito na nas nem no nos nós nossa
nosso num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem seja ser seu seus só
sua suas também te tem têm teu tua um uma umas uns você vocês vos
art arts artigo artigos lei leis decreto dispõe dispor dispositivo dispositivos altera alterar alterada
acrescenta acrescentar acrescido inclui incluir institui instituir estabelece estabelecer outras outros
providências providencias federal nacional redação nova novo parágrafo parágrafos inciso incisos alínea
caput vigor vigorar data publicação passa passam seguinte seguintes termos forma casos caso sobre
conforme deste desta dessa desse demais âmbito fins sendo bem
janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro""".split())


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def carregar(base_path: Path, emb_dir: Path, modelo: str):
    u = pd.read_parquet(emb_dir / "textos_unicos.parquet")
    emb = np.load(emb_dir / f"emb_{modelo}.npy")
    assert len(u) == len(emb), "textos_unicos e embeddings com tamanhos diferentes"
    cols = ["id", "id_texto_unico", "fonte_texto", "autor1_nome"]
    base = pd.read_parquet(base_path, columns=cols)
    return u, emb, base


def umap_cache(emb: np.ndarray, modelo: str, nn: int, pasta: Path) -> np.ndarray:
    destino = pasta / f"umap_{modelo}_nn{nn}.npy"
    if destino.exists():
        return np.load(destino)
    from umap import UMAP
    print(f"UMAP {modelo} n_neighbors={nn} (só na primeira vez; depois vem do cache)...")
    t0 = time.time()
    red = UMAP(n_neighbors=nn, n_components=5, min_dist=0.0, metric="cosine",
               random_state=SEED, low_memory=True).fit_transform(emb)
    np.save(destino, red.astype(np.float32))
    print(f"  {time.time() - t0:.0f}s")
    return red


def vetorizador(nivel: str = "docs") -> CountVectorizer:
    """nivel="docs": ajustado sobre as ementas (grade); min_df corta termos raros.
    nivel="topicos": para o BERTopic, que ajusta o vetorizador sobre UM documento por tópico.
    Ali min_df/max_df contam tópicos, não ementas, então ficam desligados para não
    eliminar justamente os termos característicos de cada tópico."""
    if nivel == "topicos":
        return CountVectorizer(stop_words=list(STOP_PT), token_pattern=r"(?u)\b[^\W\d_]{3,}\b",
                               ngram_range=(1, 2), min_df=1, lowercase=True)
    return CountVectorizer(stop_words=list(STOP_PT), token_pattern=r"(?u)\b[^\W\d_]{3,}\b",
                           ngram_range=(1, 2), min_df=5, max_df=0.5, lowercase=True)


def palavras_por_topico(X: sparse.csr_matrix, labels: np.ndarray, vocab: np.ndarray, n: int = 25) -> dict:
    """c-TF-IDF no mesmo espírito do BERTopic: termos por classe, normalizados, vezes idf de classe."""
    topicos = sorted(t for t in set(labels) if t != -1)
    if not topicos:
        return {}
    idx = {t: i for i, t in enumerate(topicos)}
    linhas = np.array([idx.get(t, -1) for t in labels])
    m = linhas >= 0
    agg = sparse.csr_matrix((np.ones(m.sum()), (linhas[m], np.nonzero(m)[0])), shape=(len(topicos), X.shape[0])) @ X
    agg = sparse.csr_matrix(agg)
    tf = sparse.diags(1 / np.maximum(np.asarray(agg.sum(1)).ravel(), 1)) @ agg
    freq = np.asarray(agg.sum(0)).ravel()
    media = agg.sum() / len(topicos)
    idf = np.log(1 + media / np.maximum(freq, 1))
    ctfidf = (tf @ sparse.diags(idf)).toarray()
    return {t: list(vocab[np.argsort(-ctfidf[idx[t]])[:n]]) for t in topicos}


def npmi_medio(Xb: sparse.csc_matrix, palavras: dict, vocab_idx: dict, top: int = 10) -> float:
    N = Xb.shape[0]
    df = np.asarray(Xb.sum(0)).ravel()
    vals = []
    for ws in palavras.values():
        ids = [vocab_idx[w] for w in ws[:top] if w in vocab_idx]
        if len(ids) < 2:
            continue
        sub = Xb[:, ids]
        co = (sub.T @ sub).toarray()
        for i, j in combinations(range(len(ids)), 2):
            pij = co[i, j] / N
            if pij == 0:
                vals.append(-1.0)
                continue
            pi, pj = df[ids[i]] / N, df[ids[j]] / N
            vals.append(np.log(pij / (pi * pj)) / -np.log(pij))
    return float(np.mean(vals)) if vals else float("nan")


def diversidade(palavras: dict, top: int = 25) -> float:
    todas = [w for ws in palavras.values() for w in ws[:top]]
    return len(set(todas)) / len(todas) if todas else float("nan")


def concentracao(labels_prop: np.ndarray, base: pd.DataFrame) -> tuple[int, int]:
    """Quantos tópicos têm mais de 50% de um único primeiro autor, e mais de 50% de texto vindo do inteiro teor."""
    d = base.assign(t=labels_prop)
    d = d[d["t"] != -1]
    g = d.groupby("t")
    autor = g["autor1_nome"].agg(lambda s: s.value_counts(normalize=True).iloc[0] if len(s) else 0)
    it = g["fonte_texto"].agg(lambda s: (s == "inteiro_teor").mean())
    return int((autor > 0.5).sum()), int((it > 0.5).sum())


# --------------------------------------------------------------------------
# grade
# --------------------------------------------------------------------------

def grade(a) -> None:
    u, emb, base = carregar(a.base, a.emb, a.modelo)
    a.saida.mkdir(parents=True, exist_ok=True)
    docs = u["texto_modelo"].fillna("").tolist()
    vec = vetorizador()
    X = vec.fit_transform(docs).tocsr()
    vocab = vec.get_feature_names_out()
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    Xb = (X > 0).astype(np.float32).tocsc()
    mapa = base["id_texto_unico"].to_numpy()

    ms_opcoes = [None] + ([5] if a.com_min_samples else [])
    log = a.saida / "runs_log.csv"
    linhas = []
    for nn in a.nn:
        red = umap_cache(emb, a.modelo, nn, a.saida)
        for mcs, metodo, ms in product(a.mcs, ["eom", "leaf"], ms_opcoes):
            t0 = time.time()
            lab = HDBSCAN(min_cluster_size=mcs, min_samples=ms, cluster_selection_method=metodo).fit(red).labels_
            lab_prop = lab[mapa]
            pal = palavras_por_topico(X, lab, vocab)
            n_top = len(pal)
            tam = pd.Series(lab_prop[lab_prop != -1]).value_counts()
            c_autor, c_it = concentracao(lab_prop, base)
            r = {
                "data": time.strftime("%Y-%m-%d %H:%M"), "modelo": a.modelo, "nn": nn, "mcs": mcs,
                "metodo": metodo, "min_samples": ms if ms else "padrao",
                "n_topicos": n_top,
                "pct_outliers": round(float((lab_prop == -1).mean()), 4),
                "maior_topico_pct": round(float(tam.iloc[0] / len(lab_prop)), 4) if n_top else 1.0,
                "npmi": round(npmi_medio(Xb, pal, vocab_idx), 4),
                "diversidade": round(diversidade(pal), 4),
                "top_um_autor_50": c_autor, "top_inteiro_teor_50": c_it,
                "segundos": round(time.time() - t0, 1),
            }
            linhas.append(r)
            print(f"nn={nn:>2} mcs={mcs:>3} {metodo:<4} ms={r['min_samples']:<6} | "
                  f"tópicos {n_top:>4} | outliers {r['pct_outliers']:.1%} | maior {r['maior_topico_pct']:.1%} | "
                  f"NPMI {r['npmi']:.3f} | div {r['diversidade']:.2f} | 1 autor>50%: {c_autor} | IT>50%: {c_it}")
    df = pd.DataFrame(linhas)
    df.to_csv(log, mode="a", header=not log.exists(), index=False)

    # Sugestão automática (a decisão final é sua, depois de ler os tópicos)
    ok = df[(df["maior_topico_pct"] <= 0.10) & (df["n_topicos"] >= a.n_temas) & (df["n_topicos"] <= 5 * a.n_temas)]
    print(f"\nRuns registrados em {log}")
    if len(ok):
        ok = ok.assign(score=ok["npmi"].rank(pct=True) + ok["diversidade"].rank(pct=True)
                       - ok["pct_outliers"].rank(pct=True))
        print("\nCandidatas que respeitam as metas de granularidade e de maior tópico (melhores primeiro):")
        print(ok.sort_values("score", ascending=False)
                .drop(columns=["data", "segundos", "score"]).head(5).to_string(index=False))
    else:
        print("\nNenhuma configuração respeitou as metas de granularidade e de maior tópico. Veja o plano (Fase 3).")


# --------------------------------------------------------------------------
# final
# --------------------------------------------------------------------------

def final(a) -> None:
    from bertopic import BERTopic
    from bertopic.dimensionality import BaseDimensionalityReduction

    u, emb, base = carregar(a.base, a.emb, a.modelo)
    a.saida.mkdir(parents=True, exist_ok=True)
    red = umap_cache(emb, a.modelo, a.nn, a.saida)
    docs = u["texto_modelo"].fillna("").tolist()
    tag = f"{a.modelo}_nn{a.nn}_mcs{a.mcs}_{a.metodo}"

    # O UMAP já está em cache: o BERTopic recebe os vetores reduzidos e não reduz de novo.
    tm = BERTopic(umap_model=BaseDimensionalityReduction(),
                  hdbscan_model=HDBSCAN(min_cluster_size=a.mcs, min_samples=a.min_samples,
                                        cluster_selection_method=a.metodo),
                  vectorizer_model=vetorizador("topicos"), top_n_words=10,
                  # Com "english" (padrão) o BERTopic apaga tudo que não é ASCII: "saúde" vira "sade".
                  language="multilingual",
                  calculate_probabilities=False, verbose=True)
    topicos, _ = tm.fit_transform(docs, embeddings=red)
    topicos = np.array(topicos)
    pct_antes = float((topicos[base["id_texto_unico"].to_numpy()] == -1).mean())

    novos = np.array(tm.reduce_outliers(docs, topicos, strategy="embeddings",
                                        embeddings=red, threshold=a.limiar))
    tm.update_topics(docs, topics=novos.tolist(), vectorizer_model=vetorizador("topicos"))
    mapa = base["id_texto_unico"].to_numpy()
    pct_depois = float((novos[mapa] == -1).mean())
    print(f"Outliers no corpus: {pct_antes:.1%} antes, {pct_depois:.1%} depois do reduce_outliers")

    tm.save(a.saida / f"bertopic_{tag}", serialization="pickle")
    info = tm.get_topic_info()
    info.to_csv(a.saida / f"topic_info_{tag}.csv", index=False)
    # Guarda os termos agora: o reduce_topics abaixo renumera os tópicos do modelo.
    termos = {t: [w for w, _ in (tm.get_topic(t) or [])][:10] for t in info["Topic"]}

    out = base[["id", "id_texto_unico"]].copy()
    out["topico_hdbscan"] = topicos[mapa]
    out["topico"] = novos[mapa]

    # Versão na granularidade dos temas oficiais, para comparar na Fase 4
    tm.reduce_topics(docs, nr_topics=a.k_reduzido + 1)   # +1 por causa do tópico -1
    out[f"topico_k{a.k_reduzido}"] = np.array(tm.topics_)[mapa]
    out.to_parquet(a.saida / f"topicos_{tag}.parquet", index=False)

    # Leitura qualitativa: termos, concentração e ementas representativas por tópico
    d = base.assign(t=out["topico"].to_numpy(), texto=u["texto_modelo"].to_numpy()[mapa])
    linhas = [f"# Leitura dos tópicos: {tag}\n",
              f"Outliers: {pct_antes:.1%} antes e {pct_depois:.1%} depois do reduce_outliers "
              f"(limiar {a.limiar}). Tópicos: {(info['Topic'] != -1).sum()}.\n",
              "Para cada tópico: está coeso? o rótulo faz sentido? algum autor ou formato domina?\n"]
    rng = np.random.default_rng(SEED)
    for _, r in info[info["Topic"] != -1].iterrows():
        t = r["Topic"]
        g = d[d["t"] == t]
        top_aut = g["autor1_nome"].value_counts(normalize=True)
        alerta = []
        if len(top_aut) and top_aut.iloc[0] > 0.5:
            alerta.append(f"{top_aut.index[0]} assina {top_aut.iloc[0]:.0%}")
        it = (g["fonte_texto"] == "inteiro_teor").mean()
        if it > 0.5:
            alerta.append(f"{it:.0%} vindos do inteiro teor")
        linhas.append(f"## Tópico {t} (n = {len(g)}){' | ATENÇÃO: ' + '; '.join(alerta) if alerta else ''}\n")
        linhas.append("Termos: " + ", ".join(termos.get(t, [])) + "\n")
        ex = g["texto"].drop_duplicates()
        for e in ex.sample(min(5, len(ex)), random_state=int(rng.integers(1e6))):
            linhas.append(f"- {str(e)[:220]}")
        linhas.append("")
    (a.saida / f"leitura_topicos_{tag}.md").write_text("\n".join(linhas), encoding="utf-8")

    resumo = {"tag": tag, "pct_outliers_antes": round(pct_antes, 4), "pct_outliers_depois": round(pct_depois, 4),
              "n_topicos": int((info["Topic"] != -1).sum()), "limiar_reduce_outliers": a.limiar,
              "k_reduzido": a.k_reduzido}
    (a.saida / f"resumo_{tag}.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")
    print(json.dumps(resumo, indent=2))
    print(f"Leia {a.saida / f'leitura_topicos_{tag}.md'} antes de seguir para a Fase 4.")


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("grade", "final"):
        s = sub.add_parser(nome)
        s.add_argument("--modelo", required=True, choices=["bertimbau", "e5"])
        s.add_argument("--base", required=True, type=Path)
        s.add_argument("--emb", default="data/processed/embeddings", type=Path)
        s.add_argument("--saida", default="data/processed/fase3", type=Path)
    g = sub.choices["grade"]
    g.add_argument("--nn", type=int, nargs="+", default=[15, 30])
    g.add_argument("--mcs", type=int, nargs="+", default=[15, 30, 50, 100])
    g.add_argument("--com-min-samples", action="store_true", help="também testa min_samples=5")
    g.add_argument("--n-temas", type=int, default=32, help="nº de temas oficiais, referência de granularidade")
    f = sub.choices["final"]
    f.add_argument("--nn", type=int, required=True)
    f.add_argument("--mcs", type=int, required=True)
    f.add_argument("--metodo", choices=["eom", "leaf"], required=True)
    f.add_argument("--min-samples", type=int, default=None)
    f.add_argument("--limiar", type=float, default=0.0,
                   help="similaridade mínima para o reduce_outliers reatribuir um outlier")
    f.add_argument("--k-reduzido", type=int, default=32)
    a = ap.parse_args()
    grade(a) if a.cmd == "grade" else final(a)


if __name__ == "__main__":
    main()
