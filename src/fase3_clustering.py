"""
fase3_clustering.py

Fase 3 do TCC: redução (UMAP), agrupamento (HDBSCAN) e escolha da configuração.
A escolha usa só métricas intrínsecas. O codTema NÃO é lido aqui, para que a
avaliação da Fase 4 seja honesta.

O UMAP e o HDBSCAN são ajustados só nas ementas substantivas. As proposições com
ementa formulaica (cujo texto vem da justificação do inteiro teor) entram depois,
no comando final, pelo tópico de centroide mais próximo. Assim elas não formam
tópicos próprios por causa do formato do texto.

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
import hashlib
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
    """Devolve (u, emb, base, form_u).
    u: textos únicos (linha i = vetor i); base: uma linha por proposição;
    form_u[i] = True quando o texto único i pertence só a proposições formulaicas."""
    u = pd.read_parquet(emb_dir / "textos_unicos.parquet")
    emb = np.load(emb_dir / f"emb_{modelo}.npy")
    if len(u) != len(emb):
        raise SystemExit("textos_unicos e embeddings com tamanhos diferentes. Rode src/fase3_embeddings.py --refazer.")
    base = pd.read_parquet(base_path)
    col = "texto_embedding" if ("texto_embedding" in base.columns and "texto_embedding" in u.columns) else "texto_modelo"
    base = base[["id", "id_texto_unico", "texto_modelo", col, "fonte_texto", "autor1_nome", "eh_formulaica"]
                if col != "texto_modelo" else
                ["id", "id_texto_unico", "texto_modelo", "fonte_texto", "autor1_nome", "eh_formulaica"]]
    # Confere se os embeddings foram gerados a partir desta base
    ref = base.drop_duplicates("id_texto_unico").set_index("id_texto_unico")[col]
    if len(ref) != len(u) or not (ref.reindex(u["id_texto_unico"]).to_numpy() == u[col].to_numpy()).all():
        raise SystemExit("A base informada não corresponde aos embeddings salvos. "
                         "Rode src/fase3_embeddings.py com esta base e --refazer.")
    form_u = base.groupby("id_texto_unico")["eh_formulaica"].all().reindex(u["id_texto_unico"]).to_numpy()
    base = base.drop(columns=[c for c in ("texto_modelo", "texto_embedding") if c in base.columns])
    return u, emb, base, form_u


def assinatura(emb: np.ndarray) -> str:
    """Identifica o conjunto de vetores usado no UMAP, para o cache nunca servir dados antigos."""
    passo = max(1, len(emb) // 500)
    return hashlib.md5(np.ascontiguousarray(emb[::passo]).tobytes() + str(emb.shape).encode()).hexdigest()[:8]


def umap_cache(emb: np.ndarray, modelo: str, nn: int, pasta: Path) -> np.ndarray:
    destino = pasta / f"umap_{modelo}_nn{nn}_{assinatura(emb)}.npy"
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


def subconjunto_ajuste(u: pd.DataFrame, base: pd.DataFrame, form_u: np.ndarray):
    """O modelo é ajustado só nas ementas substantivas. Devolve os índices dos textos
    de ajuste, a parte da base correspondente e o mapa proposição -> posição no ajuste."""
    idx_fit = np.nonzero(~form_u)[0]
    pos = np.full(len(u), -1)
    pos[idx_fit] = np.arange(len(idx_fit))
    base_fit = base[~form_u[base["id_texto_unico"].to_numpy()]]
    mapa_fit = pos[base_fit["id_texto_unico"].to_numpy()]
    return idx_fit, base_fit, mapa_fit


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
    u, emb, base_todo, form_u = carregar(a.base, a.emb, a.modelo)
    a.saida.mkdir(parents=True, exist_ok=True)
    idx_fit, base, mapa = subconjunto_ajuste(u, base_todo, form_u)
    print(f"Ajuste em {len(idx_fit)} textos únicos ({len(base)} proposições); "
          f"{int(form_u.sum())} textos de formulaicas ficam de fora e são atribuídos no comando final.")
    docs = u["texto_modelo"].fillna("").to_numpy()[idx_fit].tolist()
    vec = vetorizador()
    X = vec.fit_transform(docs).tocsr()
    vocab = vec.get_feature_names_out()
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    Xb = (X > 0).astype(np.float32).tocsc()

    ms_opcoes = [None if v == "padrao" else int(v) for v in a.min_samples]
    log = a.saida / "runs_log.csv"
    linhas = []
    for nn in a.nn:
        red = umap_cache(emb[idx_fit], a.modelo, nn, a.saida)
        for mcs, metodo, ms in product(a.mcs, a.metodos, ms_opcoes):
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
    """Ajusta o BERTopic nas ementas substantivas, reatribui os outliers e atribui as
    formulaicas ao tópico de centroide mais próximo (cosseno nos embeddings originais)."""
    from bertopic import BERTopic
    from bertopic.dimensionality import BaseDimensionalityReduction

    u, emb, base, form_u = carregar(a.base, a.emb, a.modelo)
    a.saida.mkdir(parents=True, exist_ok=True)
    idx_fit, base_fit, _ = subconjunto_ajuste(u, base, form_u)
    idx_form = np.nonzero(form_u)[0]
    red = umap_cache(emb[idx_fit], a.modelo, a.nn, a.saida)
    textos = u["texto_modelo"].fillna("").to_numpy()
    docs = textos[idx_fit].tolist()
    tag = f"{a.modelo}_nn{a.nn}_mcs{a.mcs}_{a.metodo}_ms{a.min_samples or 'padrao'}"
    tag += {"knn": "_rk", "original": "_ro", "umap": ""}[a.reatribuicao]   # sufixo por método de reatribuição

    # O UMAP já está em cache: o BERTopic recebe os vetores reduzidos e não reduz de novo.
    tm = BERTopic(umap_model=BaseDimensionalityReduction(),
                  hdbscan_model=HDBSCAN(min_cluster_size=a.mcs, min_samples=a.min_samples,
                                        cluster_selection_method=a.metodo),
                  vectorizer_model=vetorizador("topicos"), top_n_words=10,
                  # Com "english" (padrão) o BERTopic apaga tudo que não é ASCII: "saúde" vira "sade".
                  language="multilingual",
                  calculate_probabilities=False, verbose=True)
    hdb_fit, _ = tm.fit_transform(docs, embeddings=red)
    hdb_fit = np.array(hdb_fit)
    sim_out = np.full(len(idx_fit), np.nan)
    conf_out = np.full(len(idx_fit), np.nan)
    if (hdb_fit == -1).any() and a.reatribuicao == "knn":
        # Voto dos k vizinhos mais próximos do núcleo do HDBSCAN, no espaço ORIGINAL dos embeddings,
        # com peso igual à similaridade. Na comparação de 01/11 (BERTimbau), foi melhor que o centroide
        # no espaço original e que o reduce_outliers no UMAP em todas as medidas, inclusive nas apensadas,
        # que não dependem do codTema.
        En = emb[idx_fit] / np.linalg.norm(emb[idx_fit], axis=1, keepdims=True)
        nucleo = np.nonzero(hdb_fit != -1)[0]
        Ec, yc = En[nucleo], hdb_fit[nucleo]
        T = int(yc.max()) + 1
        io = np.nonzero(hdb_fit == -1)[0]
        k = a.k_vizinhos
        novos_fit = hdb_fit.copy()
        for s0 in range(0, len(io), 1000):
            bloco = io[s0:s0 + 1000]
            S = En[bloco] @ Ec.T
            nb = np.argpartition(-S, k, axis=1)[:, :k]
            w = np.take_along_axis(S, nb, 1)
            M = np.zeros((len(bloco), T))
            np.add.at(M, (np.repeat(np.arange(len(bloco)), k), yc[nb].ravel()), w.ravel())
            novos_fit[bloco] = M.argmax(1)
            conf_out[bloco] = M.max(1) / M.sum(1)          # fração (ponderada) dos votos no tópico escolhido
        Cn = np.vstack([En[nucleo][yc == t].mean(0) for t in range(T)])
        Cn /= np.linalg.norm(Cn, axis=1, keepdims=True)
        sim_out[io] = (En[io] * Cn[novos_fit[io]]).sum(1)  # similaridade com o centroide do tópico escolhido
        tm.update_topics(docs, topics=novos_fit.tolist(), vectorizer_model=vetorizador("topicos"))
    elif (hdb_fit == -1).any() and a.reatribuicao == "original":
        # Cada outlier vai para o tópico cujo centroide (média do núcleo do HDBSCAN) é o mais
        # parecido no espaço ORIGINAL dos embeddings. A anotação de 100 outliers mostrou que a
        # escolha no espaço do UMAP (padrão do reduce_outliers) erra mais.
        En = emb[idx_fit] / np.linalg.norm(emb[idx_fit], axis=1, keepdims=True)
        tops = sorted(t for t in set(hdb_fit) if t != -1)
        Cn = np.vstack([En[hdb_fit == t].mean(0) for t in tops])
        Cn /= np.linalg.norm(Cn, axis=1, keepdims=True)
        io = np.nonzero(hdb_fit == -1)[0]
        S_out = En[io] @ Cn.T
        novos_fit = hdb_fit.copy()
        escolha = np.array(tops)[S_out.argmax(1)]
        sim_out[io] = S_out.max(1)
        escolha[sim_out[io] < a.limiar] = -1
        novos_fit[io] = escolha
        tm.update_topics(docs, topics=novos_fit.tolist(), vectorizer_model=vetorizador("topicos"))
    elif (hdb_fit == -1).any():
        novos_fit = np.array(tm.reduce_outliers(docs, hdb_fit, strategy="embeddings",
                                                embeddings=red, threshold=a.limiar))
        tm.update_topics(docs, topics=novos_fit.tolist(), vectorizer_model=vetorizador("topicos"))
    else:
        novos_fit = hdb_fit.copy()

    tm.save(a.saida / f"bertopic_{tag}", serialization="pickle")
    info = tm.get_topic_info()
    info.to_csv(a.saida / f"topic_info_{tag}.csv", index=False)
    # Guarda os termos agora: o reduce_topics abaixo renumera os tópicos do modelo.
    termos = {t: [w for w, _ in (tm.get_topic(t) or [])][:10] for t in info["Topic"]}

    # Tópico, origem e similaridade por texto único
    topico_u = np.full(len(u), -1)
    hdb_u = np.full(len(u), -1)
    origem_u = np.full(len(u), "", dtype=object)
    sim_u = np.full(len(u), np.nan)
    topico_u[idx_fit] = novos_fit
    hdb_u[idx_fit] = hdb_fit
    origem_u[idx_fit] = np.where(hdb_fit != -1, "hdbscan", "reduce_outliers")
    sim_u[idx_fit] = sim_out          # similaridade do outlier com o centroide do tópico recebido
    conf_u = np.full(len(u), np.nan)
    conf_u[idx_fit] = conf_out        # consenso dos vizinhos (só na reatribuição "knn")

    # Formulaicas: centroide mais próximo no espaço original dos embeddings
    topicos_validos = sorted(t for t in set(novos_fit) if t != -1)
    if len(idx_form) and topicos_validos:
        E = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        C = np.vstack([E[idx_fit[novos_fit == t]].mean(0) for t in topicos_validos])
        C /= np.linalg.norm(C, axis=1, keepdims=True)
        S = E[idx_form] @ C.T
        topico_u[idx_form] = np.array(topicos_validos)[S.argmax(1)]
        sim_u[idx_form] = S.max(1)
        origem_u[idx_form] = "formulaica_centroide"

    # Estratégia alternativa para as formulaicas: c-TF-IDF (palavras da justificação x termos do tópico).
    # As duas estratégias são comparadas contra o codTema na Fase 4.
    alt_u = topico_u.copy()
    if len(idx_form):
        # Mesmo cálculo da estratégia "c-tf-idf" do reduce_outliers, feito à mão porque o BERTopic
        # recusa reatribuir quando o modelo já não tem tópico -1.
        from sklearn.metrics.pairwise import cosine_similarity
        bow = tm.vectorizer_model.transform(textos[idx_form].tolist())
        doc_ctf = tm.ctfidf_model.transform(bow)
        ids_top = sorted(t for t in set(tm.topics_) if t != -1)
        top_ctf = tm.c_tf_idf_[tm._outliers:][:len(ids_top)]
        sim_alt = cosine_similarity(doc_ctf, top_ctf)
        escolha = np.array(ids_top)[sim_alt.argmax(1)]
        sem_vocab = np.asarray(bow.sum(1)).ravel() == 0          # sem nenhuma palavra do vocabulário
        escolha[sem_vocab] = topico_u[idx_form][sem_vocab]       # mantém o centroide nesses casos
        alt_u[idx_form] = escolha
        conc = float((alt_u[idx_form] == topico_u[idx_form]).mean())
        print(f"Formulaicas: centroide e c-TF-IDF concordam em {conc:.0%} dos casos")

    mapa = base["id_texto_unico"].to_numpy()
    eh_form = form_u[mapa]
    out = base[["id", "id_texto_unico"]].copy()
    out["topico_hdbscan"] = hdb_u[mapa]
    out["topico"] = topico_u[mapa]
    out["origem_topico"] = origem_u[mapa]
    out["sim_centroide"] = sim_u[mapa]
    out["consenso_knn"] = conf_u[mapa]
    out["topico_alt_ctfidf"] = alt_u[mapa]

    pct_antes = float((hdb_u[mapa][~eh_form] == -1).mean())
    pct_depois = float((topico_u[mapa] == -1).mean())
    print(f"Outliers entre as proposições do ajuste: {pct_antes:.1%} antes do reduce_outliers; "
          f"no corpus inteiro depois da reatribuição: {pct_depois:.1%}")

    # Versão na granularidade dos temas oficiais, para comparar na Fase 4
    tm.reduce_topics(docs, nr_topics=a.k_reduzido + 1)   # +1 por causa do tópico -1
    reduz_fit = np.array(tm.topics_)
    de_para = pd.Series(reduz_fit).groupby(novos_fit).agg(lambda s: s.mode().iloc[0]).to_dict()
    out[f"topico_k{a.k_reduzido}"] = out["topico"].map(de_para).fillna(-1).astype(int)
    out[f"topico_alt_ctfidf_k{a.k_reduzido}"] = out["topico_alt_ctfidf"].map(de_para).fillna(-1).astype(int)
    out.to_parquet(a.saida / f"topicos_{tag}.parquet", index=False)

    # Leitura qualitativa: termos, concentração e ementas representativas por tópico
    d = base.assign(t=out["topico"].to_numpy(), texto=textos[mapa], origem=out["origem_topico"].to_numpy())
    sims = sim_u[idx_form] if len(idx_form) else np.array([np.nan])
    linhas = [f"# Leitura dos tópicos: {tag}\n",
              f"Ajuste em {len(base_fit)} proposições (ementas substantivas). Outliers do HDBSCAN: {pct_antes:.1%}, "
              f"reatribuídos pelo reduce_outliers (limiar {a.limiar}). Tópicos: {(info['Topic'] != -1).sum()}.\n",
              f"Formulaicas atribuídas pelo centroide mais próximo: {int(eh_form.sum())} proposições; "
              f"similaridade mediana {np.nanmedian(sims):.3f} (p10 {np.nanpercentile(sims, 10):.3f}).\n",
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
        n_f = int((g["origem"] == "formulaica_centroide").sum())
        cab = f"## Tópico {t} (n = {len(g)}; formulaicas atribuídas: {n_f})"
        linhas.append(cab + (" | ATENÇÃO: " + "; ".join(alerta) if alerta else "") + "\n")
        linhas.append("Termos: " + ", ".join(termos.get(t, [])) + "\n")
        nucleo = g.loc[g["origem"] == "hdbscan", "texto"].drop_duplicates()
        for e in nucleo.sample(min(5, len(nucleo)), random_state=int(rng.integers(1e6))):
            linhas.append(f"- {str(e)[:220]}")
        form = g.loc[g["origem"] == "formulaica_centroide", "texto"].drop_duplicates()
        for e in form.sample(min(2, len(form)), random_state=int(rng.integers(1e6))):
            linhas.append(f"- [formulaica] {str(e)[:220]}")
        linhas.append("")
    (a.saida / f"leitura_topicos_{tag}.md").write_text("\n".join(linhas), encoding="utf-8")

    resumo = {"tag": tag, "n_proposicoes_ajuste": int(len(base_fit)),
              "pct_outliers_hdbscan": round(pct_antes, 4), "pct_sem_topico_final": round(pct_depois, 4),
              "n_topicos": int((info["Topic"] != -1).sum()), "limiar_reduce_outliers": a.limiar,
              "n_formulaicas_atribuidas": int(eh_form.sum()),
              "sim_centroide_mediana": None if np.isnan(sims).all() else round(float(np.nanmedian(sims)), 4),
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
        s.add_argument("--modelo", required=True, choices=["bertimbau", "e5", "serafim", "serafim900"])
        s.add_argument("--base", required=True, type=Path)
        s.add_argument("--emb", default="data/processed/embeddings", type=Path)
        s.add_argument("--saida", default="data/processed/fase3", type=Path)
    g = sub.choices["grade"]
    g.add_argument("--nn", type=int, nargs="+", default=[15, 30])
    g.add_argument("--mcs", type=int, nargs="+", default=[15, 30, 50, 100])
    g.add_argument("--metodos", nargs="+", default=["eom", "leaf"], choices=["eom", "leaf"])
    g.add_argument("--min-samples", nargs="+", default=["padrao"],
                   help='valores de min_samples; "padrao" = igual ao min_cluster_size. Ex.: padrao 5 10')
    g.add_argument("--n-temas", type=int, default=32, help="nº de temas oficiais, referência de granularidade")
    f = sub.choices["final"]
    f.add_argument("--nn", type=int, required=True)
    f.add_argument("--mcs", type=int, required=True)
    f.add_argument("--metodo", choices=["eom", "leaf"], required=True)
    f.add_argument("--min-samples", type=int, default=None)
    f.add_argument("--limiar", type=float, default=0.0,
                   help="similaridade mínima para o reduce_outliers reatribuir um outlier")
    f.add_argument("--k-reduzido", type=int, default=32)
    f.add_argument("--reatribuicao", choices=["knn", "original", "umap"], default="knn",
                   help='"knn" (padrão): voto dos k vizinhos do núcleo no espaço original (sufixo _rk); '
                        '"original": centroide do núcleo no espaço original (_ro); '
                        '"umap": reduce_outliers do BERTopic no espaço reduzido (sem sufixo, versão antiga)')
    f.add_argument("--k-vizinhos", type=int, default=15, help="vizinhos do núcleo que votam na reatribuição knn")
    a = ap.parse_args()
    grade(a) if a.cmd == "grade" else final(a)


if __name__ == "__main__":
    main()
