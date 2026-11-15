"""
robustez_modelos.py

Extra da revisão do TCC (09/11/2026). Complementa a Fase 4 com quatro análises:

  tabela      avaliação lado a lado dos três modelos (BCubed natural, reduzido a 32 e só o núcleo,
              referências aleatórias, pureza), a partir dos CSVs que a Fase 4 já gerou.
  bootstrap   IC de 95% do BCubed de cada modelo e das diferenças entre modelos, por reamostragem
              de proposições (a variação medida é a de amostragem; a do UMAP fica em `sementes`).
  apensadas   teto da validação pelas apensadas: fração dos pares que compartilham tema oficial e
              fração que ficaria no mesmo grupo no teto prático, ao lado dos modelos.
  sementes    refaz UMAP, HDBSCAN e reatribuição (15 vizinhos) com outras sementes do UMAP e mede
              a variação das métricas. Formulaicas pelo centroide (a diferença para o c-TF-IDF
              é de até 0,003 no BCubed). A semente principal (SEED, 130) reaproveita o UMAP em cache e serve de
              conferência: tem que reproduzir os números da Fase 4.
  resumo      média e desvio-padrão das sementes, por modelo.

Uso (a partir de code/):
    python src/extras/robustez_modelos.py tabela
    python src/extras/robustez_modelos.py bootstrap --b 2000
    python src/extras/robustez_modelos.py apensadas
    python src/extras/robustez_modelos.py sementes --modelos bertimbau serafim e5   (sementes 130 a 134, de src/seed.py)
    python src/extras/robustez_modelos.py resumo

Saídas em data/processed/fase4/robustez/.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fase4_avaliacao import Gabarito, unitarios            # noqa: E402
from seed import SEED, SEMENTES_ESTABILIDADE                # noqa: E402

MODELOS = {                        # nome no texto -> (tag dos arquivos da Fase 3, mcs, min_samples)
    "BERTimbau": ("bertimbau_nn30_mcs100_eom_ms10_rk", 100, 10),
    "Serafim": ("serafim_nn30_mcs100_eom_ms5_rk", 100, 5),
    "e5": ("e5_nn30_mcs100_eom_ms10_rk", 100, 10),
}
CHAVE = {"bertimbau": "BERTimbau", "serafim": "Serafim", "e5": "e5"}
BASE = sorted(Path("data/processed").glob("base_fase2_*.parquet"))[-1]   # a base da Fase 2 mais recente
TEMAS = Path("data/processed/temas_long_20261027.parquet")
FASE3 = Path("data/processed/fase3")
FASE4 = Path("data/processed/fase4")
EMB = Path("data/processed/embeddings")
SAIDA = FASE4 / "robustez"


def base_com_temas(base_path: Path = BASE, temas_path: Path = TEMAS):
    base = pd.read_parquet(base_path, columns=["id", "siglaTipo", "eh_formulaica", "idPropPrincipal"])
    temas = pd.read_parquet(temas_path)
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    base = base[base["id"].isin(conj.index)].reset_index(drop=True)
    base["temas"] = base["id"].map(conj)
    return base, temas


def pares_apensadas(base: pd.DataFrame) -> pd.DataFrame:
    p = base[base["idPropPrincipal"].notna()][["id", "idPropPrincipal"]].copy()
    p["idPropPrincipal"] = p["idPropPrincipal"].astype(int)
    return p[p["idPropPrincipal"].isin(base["id"])]


def mesmo_topico(base: pd.DataFrame, pares: pd.DataFrame, topico: np.ndarray) -> float:
    s = pd.Series(topico, index=base["id"].to_numpy())
    return float((s.loc[pares["id"]].to_numpy() == s.loc[pares["idPropPrincipal"]].to_numpy()).mean())


# ---------------------------------------------------------------- tabela

def tabela(a) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    res = pd.read_csv(FASE4 / "bcubed_resultados.csv")
    linhas = []
    for nome, (tag, _, _) in MODELOS.items():
        r = res[res["modelo"] == tag]
        conv = pd.read_csv(FASE4 / f"convergencia_{tag}.csv")
        def pega(versao, gran):
            x = r[(r["versao"] == versao) & (r["granularidade"] == gran)].iloc[0]
            return x
        for rotulo, versao, gran in [
            ("natural (outliers reatribuídos)", "outliers reatribuídos; formulaicas por c-TF-IDF", "natural"),
            ("reduzido a 32 tópicos", "outliers reatribuídos; formulaicas por c-TF-IDF", "k32"),
            ("só o núcleo (outliers como grupos unitários)", "outliers como grupos unitários", "natural"),
            ("aleatório, mesmos tamanhos (natural)", "aleatório, mesmos tamanhos (5 sementes)", "natural"),
            ("aleatório, mesmos tamanhos (k32)", "aleatório, mesmos tamanhos (5 sementes)", "k32"),
        ]:
            x = pega(versao, gran)
            linhas.append({"modelo": nome, "versao": rotulo, "grupos": int(x["n_grupos"]),
                           "P": x["P"], "R": x["R"], "F": x["F"],
                           "pureza_mediana": round(float(conv["pureza"].median()), 3) if "natural" in rotulo and "aleat" not in rotulo else ""})
    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA / "tabela_modelos.csv", index=False)
    print(out.to_string(index=False))


# ---------------------------------------------------------------- bootstrap

def bootstrap(a) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    base, _ = base_com_temas()
    gab = Gabarito(list(base["temas"]))
    itens = {}
    for nome, (tag, _, _) in MODELOS.items():
        t = pd.read_parquet(FASE3 / f"topicos_{tag}.parquet")
        d = base[["id"]].merge(t, on="id", validate="one_to_one")
        assert len(d) == len(base)
        P, R = gab.por_item(d["topico_alt_ctfidf"].to_numpy())
        itens[nome] = (P, R)
        print(f"{nome}: P={P.mean():.3f} R={R.mean():.3f}")
    rng = np.random.default_rng(SEED)
    n, B = len(base), a.b
    nomes = list(itens)
    est = {m: np.zeros((B, 3)) for m in nomes}
    for b in range(B):
        ix = rng.integers(0, n, n)
        for m in nomes:
            p, r = itens[m][0][ix].mean(), itens[m][1][ix].mean()
            est[m][b] = (p, r, 2 * p * r / (p + r))
    linhas = []
    for m in nomes:
        for j, met in enumerate(("P", "R", "F")):
            lo, hi = np.percentile(est[m][:, j], [2.5, 97.5])
            linhas.append({"comparacao": m, "metrica": met, "estimativa": round(float(est[m][:, j].mean()), 4),
                           "ic95_inf": round(float(lo), 4), "ic95_sup": round(float(hi), 4), "p_maior_que_0": ""})
    for ref in ("Serafim", "e5"):
        for j, met in enumerate(("P", "R", "F")):
            dif = est["BERTimbau"][:, j] - est[ref][:, j]
            lo, hi = np.percentile(dif, [2.5, 97.5])
            linhas.append({"comparacao": f"BERTimbau - {ref}", "metrica": met, "estimativa": round(float(dif.mean()), 4),
                           "ic95_inf": round(float(lo), 4), "ic95_sup": round(float(hi), 4),
                           "p_maior_que_0": round(float((dif > 0).mean()), 4)})
    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA / "bootstrap_bcubed.csv", index=False)
    print(out.to_string(index=False))


# ---------------------------------------------------------------- apensadas

def apensadas(a) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    base, temas = base_com_temas()
    pares = pares_apensadas(base)
    s = base.set_index("id")["temas"]
    comp = np.mean([len(x & y) > 0 for x, y in zip(s.loc[pares["id"]], s.loc[pares["idPropPrincipal"]])])
    freq = temas["codTema"].value_counts().to_dict()
    teto = np.array([max(x, key=lambda t: freq[t]) for x in base["temas"]])
    linhas = [{"item": "pares apensada e principal (com tema oficial)", "valor": len(pares)},
              {"item": "compartilham ao menos um tema oficial", "valor": round(float(comp), 4)},
              {"item": "no mesmo grupo no teto prático (tema mais frequente)", "valor": round(mesmo_topico(base, pares, teto), 4)}]
    for nome, (tag, _, _) in MODELOS.items():
        t = pd.read_parquet(FASE3 / f"topicos_{tag}.parquet")
        d = base[["id"]].merge(t, on="id", validate="one_to_one")
        top = d["topico"].to_numpy()
        obs = mesmo_topico(base, pares, top)
        rng = np.random.default_rng(SEED)
        aleat = np.mean([mesmo_topico(base, pares, rng.permutation(top)) for _ in range(5)])
        # entre os pares que compartilham tema, quantos caem no mesmo tópico
        st = pd.Series(top, index=base["id"].to_numpy())
        ok = np.array([len(x & y) > 0 for x, y in zip(s.loc[pares["id"]], s.loc[pares["idPropPrincipal"]])])
        juntos = st.loc[pares["id"]].to_numpy() == st.loc[pares["idPropPrincipal"]].to_numpy()
        linhas += [{"item": f"{nome}: no mesmo tópico", "valor": round(obs, 4)},
                   {"item": f"{nome}: no mesmo tópico, aleatório com os mesmos tamanhos", "valor": round(float(aleat), 4)},
                   {"item": f"{nome}: no mesmo tópico, só pares que compartilham tema", "valor": round(float(juntos[ok].mean()), 4)}]
    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA / "apensadas_teto.csv", index=False)
    print(out.to_string(index=False))


# ---------------------------------------------------------------- sementes

def sementes(a) -> None:
    import fase3_clustering as fc
    from sklearn.cluster import HDBSCAN
    from umap import UMAP

    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = SAIDA / "sementes.csv"
    feitos = set()
    if destino.exists():
        df0 = pd.read_csv(destino)
        feitos = set(zip(df0["modelo"], df0["semente"]))
    base, _ = base_com_temas()
    gab = Gabarito(list(base["temas"]))
    pares = pares_apensadas(base)

    for chave in a.modelos:
        nome = CHAVE[chave]
        _, mcs, ms = MODELOS[nome]
        u, emb, b2, form_u = fc.carregar(BASE, EMB, chave)
        idx_fit, _, _ = fc.subconjunto_ajuste(u, b2, form_u)
        idx_form = np.nonzero(form_u)[0]
        E = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        En = E[idx_fit]
        mapa = b2["id_texto_unico"].to_numpy()
        for seed in a.sementes:
            if (nome, seed) in feitos:
                print(f"{nome} semente {seed}: já feito")
                continue
            t0 = time.time()
            cache = FASE3 / f"umap_{chave}_nn30_s{fc.SEED}_{fc.assinatura(emb[idx_fit])}.npy"
            if seed == fc.SEED and cache.exists():       # a semente principal reaproveita o UMAP da Fase 3
                red = np.load(cache)
            else:
                red = UMAP(n_neighbors=30, n_components=5, min_dist=0.0, metric="cosine",
                           random_state=seed, low_memory=True).fit_transform(emb[idx_fit])
            t_umap = time.time() - t0
            hdb = HDBSCAN(min_cluster_size=mcs, min_samples=ms, cluster_selection_method="eom").fit(red).labels_
            novos = hdb.copy()
            io = np.nonzero(hdb == -1)[0]
            nucleo = np.nonzero(hdb != -1)[0]
            Ec, yc = En[nucleo], hdb[nucleo]
            T = int(yc.max()) + 1
            k = 15
            for s0 in range(0, len(io), 1000):
                bl = io[s0:s0 + 1000]
                S = En[bl] @ Ec.T
                nb = np.argpartition(-S, k, axis=1)[:, :k]
                w = np.take_along_axis(S, nb, 1)
                M = np.zeros((len(bl), T))
                np.add.at(M, (np.repeat(np.arange(len(bl)), k), yc[nb].ravel()), w.ravel())
                novos[bl] = M.argmax(1)
            topico_u = np.full(len(u), -1)
            hdb_u = np.full(len(u), -1)
            topico_u[idx_fit] = novos
            hdb_u[idx_fit] = hdb
            tops = sorted(set(novos))
            C = np.vstack([En[novos == t].mean(0) for t in tops])
            C /= np.linalg.norm(C, axis=1, keepdims=True)
            topico_u[idx_form] = np.array(tops)[(E[idx_form] @ C.T).argmax(1)]

            d = pd.DataFrame({"id": b2["id"].to_numpy(), "topico": topico_u[mapa], "hdb": hdb_u[mapa],
                              "form": form_u[mapa]})
            d = base[["id"]].merge(d, on="id", validate="one_to_one")
            r = gab.bcubed(d["topico"].to_numpy())
            subst = ~d["form"].to_numpy()
            linha = {"modelo": nome, "semente": seed, "n_topicos": int(d["topico"].nunique()),
                     "outliers_pct": round(float((d.loc[subst, "hdb"] == -1).mean() * 100), 1),
                     "P": round(r["P"], 4), "R": round(r["R"], 4), "F": round(r["F"], 4),
                     "apensadas_pct": round(mesmo_topico(base, pares, d["topico"].to_numpy()) * 100, 1),
                     "seg_umap": round(t_umap), "seg_total": round(time.time() - t0)}
            print(linha, flush=True)
            pd.DataFrame([linha]).to_csv(destino, mode="a", header=not destino.exists(), index=False)


def resumo(a) -> None:
    df = pd.read_csv(SAIDA / "sementes.csv")
    g = df.groupby("modelo")[["n_topicos", "outliers_pct", "P", "R", "F", "apensadas_pct"]].agg(["mean", "std", "min", "max"]).round(4)
    g.to_csv(SAIDA / "sementes_resumo.csv")
    print(df.to_string(index=False)); print(); print(g.T.to_string())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("tabela").set_defaults(f=tabela)
    b = sp.add_parser("bootstrap"); b.add_argument("--b", type=int, default=2000); b.set_defaults(f=bootstrap)
    sp.add_parser("apensadas").set_defaults(f=apensadas)
    s = sp.add_parser("sementes")
    s.add_argument("--modelos", nargs="+", default=["bertimbau", "serafim", "e5"], choices=list(CHAVE))
    s.add_argument("--sementes", nargs="+", type=int, default=SEMENTES_ESTABILIDADE)
    s.set_defaults(f=sementes)
    sp.add_parser("resumo").set_defaults(f=resumo)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
