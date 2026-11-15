"""
fase4_avaliacao.py

Fase 4 do TCC: compara os tópicos com a classificação temática oficial (codTema).

Para cada arquivo de tópicos da Fase 3 informado:
  1. BCubed estendido (Amigó et al., 2009) em várias versões:
       - granularidade natural e reduzida (topico_k32);
       - outliers do HDBSCAN reatribuídos ou tratados como grupos unitários;
       - formulaicas atribuídas pelo centroide ou pelo c-TF-IDF (se a coluna existir).
     Ao lado das referências: um cluster só, cada proposição sozinha, aleatório com a
     mesma distribuição de tamanhos do modelo (média de 5 sementes) e o "teto" de um
     agrupamento rígido feito pelo tema mais frequente do próprio gabarito.
  2. Precisão e recall médios por tipo (PL, PLP, PEC) e para as formulaicas.
  3. Validação independente do codTema: pares proposição apensada e principal.
  4. Desvios temáticos: fragmentação (por tema oficial), convergência (por tópico)
     e dispersão (proposições que dividem tema com o resto do tópico menos do que o acaso).
  5. Candidatos a estudos de caso, com ementas de exemplo.

Uso (a partir de code/):
    uv run python src/fase4_avaliacao.py --base data/processed/base_fase2_20261101.parquet \
        --temas data/processed/temas_long_20261027.parquet \
        --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10.parquet \
                  data/processed/fase3/topicos_e5_nn30_mcs100_eom_ms10.parquet

Saídas em data/processed/fase4/:
    relatorio_fase4.md            tabelas principais, para ler e levar para a monografia
    bcubed_resultados.csv         todas as versões e referências
    bcubed_por_tipo.csv           P e R médios por tipo de proposição e para as formulaicas
    fragmentacao_<tag>.csv        um tema oficial por linha
    convergencia_<tag>.csv        um tópico por linha
    dispersao_<tag>.csv           proposições que dividem tema com o tópico menos do que o acaso
    matriz_topico_tema_<tag>.csv  contagens tópico x tema (base do heatmap)
    heatmap_<tag>.html            heatmap interativo (se o plotly estiver instalado)
    casos_<tag>.md                candidatos a estudos de caso
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from seed import SEED  # noqa: E402  (130; ver src/seed.py)


# --------------------------------------------------------------------------
# BCubed estendido, por item
# --------------------------------------------------------------------------

class Gabarito:
    """Pré-computa as interseções entre conjuntos de temas (assinaturas) de um conjunto de itens.
    Com um cluster por item (agrupamento rígido), para e e e' no mesmo cluster:
        precisão(e, e') = 1 se compartilham ao menos um tema
        recall(e, e')   = 1 / |L(e) ∩ L(e')|  se compartilham, senão 0
    P(e) = média da precisão sobre os itens do cluster de e;
    R(e) = soma do recall sobre o cluster / nº de itens do corpus que compartilham tema com e."""

    def __init__(self, rotulos: list[frozenset]):
        assin = sorted(set(rotulos), key=lambda s: tuple(sorted(s)))
        idx = {s: i for i, s in enumerate(assin)}
        self.sig = np.array([idx[s] for s in rotulos])
        temas = sorted(set().union(*assin))
        col = {t: j for j, t in enumerate(temas)}
        M = np.zeros((len(assin), len(temas)), dtype=np.float32)
        for s, i in idx.items():
            for t in s:
                M[i, col[t]] = 1
        O = M @ M.T
        self.comp = (O > 0).astype(np.float32)
        self.inv = np.where(O > 0, 1.0 / np.maximum(O, 1), 0.0).astype(np.float32)
        glob = np.bincount(self.sig, minlength=len(assin)).astype(np.float64)
        self.denom = self.comp @ glob
        self.n_sig = len(assin)

    def por_item(self, clusters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        n = len(clusters)
        P, R = np.empty(n), np.empty(n)
        grupos = pd.Series(np.arange(n)).groupby(clusters).indices
        for idx in grupos.values():
            s = self.sig[idx]
            cnt = np.bincount(s, minlength=self.n_sig).astype(np.float32)
            pres = np.nonzero(cnt)[0]
            p_val = np.zeros(self.n_sig); r_val = np.zeros(self.n_sig)
            p_val[pres] = self.comp[pres] @ cnt
            r_val[pres] = self.inv[pres] @ cnt
            P[idx] = p_val[s] / len(idx)
            R[idx] = r_val[s] / self.denom[s]
        return P, R

    def bcubed(self, clusters: np.ndarray) -> dict:
        P, R = self.por_item(clusters)
        p, r = float(P.mean()), float(R.mean())
        return {"P": p, "R": r, "F": 2 * p * r / (p + r) if p + r else 0.0}


def unitarios(rotulo: np.ndarray) -> np.ndarray:
    """Troca -1 por um identificador único por item (cada outlier vira um grupo de um)."""
    out = rotulo.astype(np.int64).copy()
    m = out == -1
    out[m] = -1 - np.arange(m.sum())
    return out


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def nomes_topicos(caminho_topicos: Path) -> dict:
    info = caminho_topicos.with_name(caminho_topicos.name.replace("topicos_", "topic_info_")).with_suffix(".csv")
    if not info.exists():
        return {}
    df = pd.read_csv(info)
    nomes = df.set_index("Topic")["Name"].astype(str).str.split("_", n=1).str[1].str.replace("_", ", ")
    return {int(k): v[:70] for k, v in nomes.items()}


def md(df: pd.DataFrame, index: bool = False) -> str:
    d = df.reset_index() if index else df
    linhas = ["| " + " | ".join(map(str, d.columns)) + " |", "| " + " | ".join("---" for _ in d.columns) + " |"]
    for r in d.itertuples(index=False):
        linhas.append("| " + " | ".join(str(v).replace("|", "/") for v in r) + " |")
    return "\n".join(linhas)


def entropia_norm(cont: np.ndarray) -> float:
    p = cont[cont > 0] / cont.sum()
    return float(-(p * np.log(p)).sum() / np.log(len(cont))) if len(cont) > 1 else 0.0


def n_para_cobrir(cont: pd.Series, frac: float = 0.8) -> int:
    c = cont.sort_values(ascending=False).cumsum() / cont.sum()
    return int((c < frac).sum() + 1)


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--temas", required=True, type=Path)
    ap.add_argument("--topicos", required=True, type=Path, nargs="+")
    ap.add_argument("--saida", default="data/processed/fase4", type=Path)
    ap.add_argument("--k", type=int, default=32)
    ap.add_argument("--sementes", type=int, default=5)
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    cols = ["id", "siglaTipo", "ementa", "eh_formulaica"] + \
        [c for c in ("idPropPrincipal",) if c in pd.read_parquet(a.base).columns]
    base = pd.read_parquet(a.base, columns=cols)
    temas = pd.read_parquet(a.temas)
    nome_tema = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    base = base[base["id"].isin(conj.index)].reset_index(drop=True)      # só quem tem tema oficial
    base["temas"] = base["id"].map(conj)
    print(f"{len(base)} proposições com tema oficial")
    gab = Gabarito(list(base["temas"]))

    # Referências comuns a todos os modelos
    freq = temas["codTema"].value_counts().to_dict()
    resultados = []
    def registra(modelo, versao, gran, r, n_grupos):
        resultados.append({"modelo": modelo, "versao": versao, "granularidade": gran,
                           "n_grupos": n_grupos, "P": round(r["P"], 3), "R": round(r["R"], 3), "F": round(r["F"], 3)})
        print(f"  {modelo:<28} {versao:<44} {gran:<9} P={r['P']:.3f} R={r['R']:.3f} F={r['F']:.3f}")

    print("\nReferências")
    registra("referência", "um cluster só", "-", gab.bcubed(np.zeros(len(base), dtype=int)), 1)
    registra("referência", "cada proposição sozinha", "-", gab.bcubed(np.arange(len(base))), len(base))
    teto = np.array([max(s, key=lambda t: freq[t]) for s in base["temas"]])
    registra("referência", "teto: tema mais frequente do gabarito", "-", gab.bcubed(teto), len(set(teto)))

    por_tipo, relat_modelos = [], []
    for caminho in a.topicos:
        tag = caminho.stem.replace("topicos_", "")
        nomes = nomes_topicos(caminho)
        t = pd.read_parquet(caminho)
        d = base.merge(t, on="id", how="inner", validate="one_to_one")
        if len(d) != len(base):
            raise SystemExit(f"{caminho.name}: {len(base) - len(d)} proposições sem tópico. Base e tópicos são de versões diferentes?")
        kcol = f"topico_k{a.k}"
        print(f"\n{tag}")

        versoes = [("outliers reatribuídos; formulaicas por centroide", "natural", d["topico"].to_numpy()),
                   ("outliers como grupos unitários", "natural", unitarios(d["topico_hdbscan"].to_numpy()))]
        if "topico_alt_ctfidf" in d:
            versoes.insert(1, ("outliers reatribuídos; formulaicas por c-TF-IDF", "natural", d["topico_alt_ctfidf"].to_numpy()))
        if kcol in d:
            versoes.append(("outliers reatribuídos; formulaicas por centroide", f"k{a.k}", d[kcol].to_numpy()))
        if f"topico_alt_ctfidf_k{a.k}" in d:
            versoes.append(("outliers reatribuídos; formulaicas por c-TF-IDF", f"k{a.k}", d[f"topico_alt_ctfidf_k{a.k}"].to_numpy()))

        PR_principal = None
        for nome_v, gran, cl in versoes:
            P, R = gab.por_item(cl)
            p, r = P.mean(), R.mean()
            registra(tag, nome_v, gran, {"P": p, "R": r, "F": 2 * p * r / (p + r)}, len(set(cl)))
            if PR_principal is None:
                PR_principal = (P, R)
            # médias por tipo e para as formulaicas, dentro desta versão
            for grupo, m in [*[(tp, (d["siglaTipo"] == tp).to_numpy()) for tp in ("PL", "PLP", "PEC")],
                             ("formulaicas", d["eh_formulaica"].to_numpy()),
                             ("não formulaicas", ~d["eh_formulaica"].to_numpy())]:
                if m.any():
                    por_tipo.append({"modelo": tag, "versao": nome_v, "granularidade": gran, "grupo": grupo,
                                     "n": int(m.sum()), "P_medio": round(P[m].mean(), 3), "R_medio": round(R[m].mean(), 3)})

        # Aleatório com a mesma distribuição de tamanhos do modelo
        for gran, col in (("natural", "topico"), (f"k{a.k}", kcol)):
            if col not in d:
                continue
            rs = [gab.bcubed(rng.permutation(d[col].to_numpy())) for _ in range(a.sementes)]
            registra(tag, f"aleatório, mesmos tamanhos ({a.sementes} sementes)", gran,
                     {k: float(np.mean([x[k] for x in rs])) for k in ("P", "R", "F")}, d[col].nunique())

        # ---------------- Apensadas ----------------
        apens = {}
        if "idPropPrincipal" in d:
            topo = d.set_index("id")
            pares = d[d["idPropPrincipal"].notna() & d["idPropPrincipal"].isin(topo.index)][["id", "idPropPrincipal"]]
            if len(pares):
                for gran, col in (("natural", "topico"), (f"k{a.k}", kcol)):
                    if col not in d:
                        continue
                    a1 = topo.loc[pares["id"], col].to_numpy(); a2 = topo.loc[pares["idPropPrincipal"].astype(int), col].to_numpy()
                    p_k = d[col].value_counts(normalize=True)
                    apens[gran] = {"pares": len(pares), "mesmo_topico": float((a1 == a2).mean()),
                                   "esperado_acaso": float((p_k ** 2).sum())}
                t1 = topo.loc[pares["id"], "temas"].to_numpy(); t2 = topo.loc[pares["idPropPrincipal"].astype(int), "temas"].to_numpy()
                apens["compartilham_tema"] = float(np.mean([len(x & y) > 0 for x, y in zip(t1, t2)]))

        # ---------------- Desvios ----------------
        P, R = PR_principal
        d["P_item"], d["R_item"] = P, R
        # Acaso por item: fração do corpus que divide ao menos um tema com a proposição
        d["P_acaso"] = gab.denom[gab.sig] / len(d)
        longo = d[["id", "topico", "temas"]].explode("temas").rename(columns={"temas": "codTema"}).reset_index(drop=True)
        longo["codTema"] = longo["codTema"].astype(int)
        mat = pd.crosstab(longo["topico"], longo["codTema"])
        mat.columns = [nome_tema.get(c, c) for c in mat.columns]
        mat.index = [f"{i}: {nomes.get(i, '')[:45]}" for i in mat.index]
        mat.to_csv(a.saida / f"matriz_topico_tema_{tag}.csv")

        frag = []
        for c, g in longo.groupby("codTema"):
            cont = g["topico"].value_counts()
            top3 = "; ".join(f"{i} ({v / cont.sum():.0%})" for i, v in cont.head(3).items())
            frag.append({"tema": nome_tema.get(c, c), "n": int(cont.sum()), "n_topicos": int(cont.size),
                         "topicos_para_80pct": n_para_cobrir(cont), "entropia_norm": round(entropia_norm(cont.to_numpy()), 3),
                         "maior_topico_pct": round(cont.iloc[0] / cont.sum(), 3), "principais_topicos": top3})
        frag = pd.DataFrame(frag).sort_values("entropia_norm", ascending=False)
        frag.to_csv(a.saida / f"fragmentacao_{tag}.csv", index=False)

        conv = []
        for tp, g in d.groupby("topico"):
            cont = pd.Series([x for s in g["temas"] for x in s]).value_counts()
            dominante = cont.index[0]
            conv.append({"topico": int(tp), "nome": nomes.get(int(tp), ""), "n": len(g),
                         "tema_dominante": nome_tema.get(dominante, dominante),
                         "pureza": round(float(g["temas"].map(lambda s: dominante in s).mean()), 3),
                         "temas_para_80pct": n_para_cobrir(cont), "P_medio": round(g["P_item"].mean(), 3),
                         "R_medio": round(g["R_item"].mean(), 3),
                         "principais_temas": "; ".join(f"{nome_tema.get(i, i)} ({v / len(g):.0%})" for i, v in cont.head(3).items())})
        conv = pd.DataFrame(conv).sort_values("pureza")
        conv.to_csv(a.saida / f"convergencia_{tag}.csv", index=False)

        m_disp = d["P_item"] < d["P_acaso"]
        disp = d[m_disp][["id", "topico", "ementa", "P_item", "P_acaso"]].assign(
            temas=d.loc[m_disp, "temas"].map(lambda s: "; ".join(nome_tema.get(x, str(x)) for x in sorted(s))),
            nome_topico=lambda x: x["topico"].map(nomes)).round({"P_item": 3, "P_acaso": 3})
        disp.to_csv(a.saida / f"dispersao_{tag}.csv", index=False)

        try:
            import plotly.express as px
            norm = mat.div(mat.sum(axis=1), axis=0)
            fig = px.imshow(norm, aspect="auto", color_continuous_scale="Blues",
                            labels={"x": "tema oficial", "y": "tópico", "color": "fração do tópico"},
                            title=f"Tópicos x temas oficiais ({tag})")
            fig.update_layout(height=max(600, 14 * len(norm)))
            fig.write_html(a.saida / f"heatmap_{tag}.html")
        except Exception as e:                 # plotly ausente ou erro de renderização
            print(f"  (heatmap não gerado: {e})")

        # ---------------- Casos ----------------
        casos = [f"# Candidatos a estudos de caso: {tag}\n",
                 "Leia as ementas e escolha de 3 a 5 casos para a Discussão. Os números são do BCubed por item "
                 "(P: quanto a proposição divide tema com o resto do tópico; R: quanto do seu tema ficou no mesmo tópico).\n"]
        casos.append("## Convergência: tópicos que juntam vários temas oficiais\n")
        for _, r in conv[conv["n"] >= 150].head(6).iterrows():
            casos.append(f"### Tópico {r.topico}: {r.nome} (n = {r.n}; pureza {r.pureza:.0%})\n")
            casos.append(f"Temas: {r.principais_temas}\n")
            g = d[d["topico"] == r.topico]
            for tema in pd.Series([x for s in g["temas"] for x in s]).value_counts().head(3).index:
                ex = g[g["temas"].map(lambda s: tema in s and len(s) == 1)]["ementa"]
                for e in ex.sample(min(2, len(ex)), random_state=SEED):
                    casos.append(f"- [{nome_tema.get(tema, tema)}] {e[:200]}")
            casos.append("")
        casos.append("## Fragmentação: temas oficiais espalhados por muitos tópicos\n")
        for _, r in frag[frag["n"] >= 300].head(5).iterrows():
            casos.append(f"### {r.tema} (n = {r.n}; {r.n_topicos} tópicos; {r.topicos_para_80pct} cobrem 80%)\n")
            casos.append(f"Principais tópicos: " + "; ".join(
                f"{p.split(' ')[0]} {nomes.get(int(p.split(' ')[0]), '')[:40]} {p.split(' ', 1)[1]}" for p in r.principais_topicos.split("; ")) + "\n")
        casos.append("## Dispersão\n")
        casos.append(f"{len(disp)} proposições ({len(disp) / len(d):.1%}) dividem tema oficial com o resto do tópico menos do que o acaso prevê para elas. "
                     f"Tópicos com mais casos: " + "; ".join(f"{k} ({v})" for k, v in disp["topico"].value_counts().head(5).items()) + "\n")
        for _, r in disp.sample(min(8, len(disp)), random_state=SEED).iterrows():
            casos.append(f"- tópico {r.topico} ({str(r.nome_topico)[:35]}) | temas: {r.temas} | {r.ementa[:160]}")
        (a.saida / f"casos_{tag}.md").write_text("\n".join(casos), encoding="utf-8")

        relat_modelos.append((tag, apens, frag, conv, disp, len(d)))

    # ---------------- Relatório ----------------
    res = pd.DataFrame(resultados)
    res.to_csv(a.saida / "bcubed_resultados.csv", index=False)
    pt = pd.DataFrame(por_tipo)
    pt.to_csv(a.saida / "bcubed_por_tipo.csv", index=False)
    rel = ["# Relatório da Fase 4\n",
           f"{len(base)} proposições com tema oficial; {len(temas['codTema'].unique())} temas.\n",
           "## BCubed estendido\n",
           "P = precisão, R = recall, F = média harmônica. Leia P e R separados: \"um cluster só\" tem F alto sem significar nada.\n",
           md(res), ""]
    rel += ["## Por tipo de proposição e formulaicas (versão principal)\n",
            md(pt[pt["versao"].str.contains("centroide") & (pt["granularidade"] == "natural")].drop(columns=["versao", "granularidade"])), ""]
    if not pt[pt["versao"].str.contains("c-TF-IDF")].empty:
        comp = pt[(pt["grupo"] == "formulaicas") & (pt["granularidade"] == "natural") & pt["versao"].str.contains("formulaicas por")][["modelo", "versao", "n", "P_medio", "R_medio"]]
        rel += ["## Formulaicas: centroide x c-TF-IDF\n", md(comp), ""]
    for tag, apens, frag, conv, disp, n in relat_modelos:
        rel.append(f"## {tag}\n")
        if apens:
            linhas = [f"- Pares apensada e principal: {apens['natural']['pares']}; "
                      f"{apens['compartilham_tema']:.1%} compartilham tema oficial."]
            for gran in ("natural", f"k{a.k}"):
                if gran in apens:
                    x = apens[gran]
                    linhas.append(f"- No mesmo tópico ({gran}): {x['mesmo_topico']:.1%} (acaso: {x['esperado_acaso']:.1%}).")
            rel += linhas + [""]
        rel += [f"- Dispersão: {len(disp)} proposições ({len(disp) / n:.1%}) dividem tema com o resto do tópico menos do que o acaso prevê para elas.",
                f"- Pureza mediana dos tópicos: {conv['pureza'].median():.0%}; "
                f"tópicos com pureza abaixo de 50%: {int((conv['pureza'] < .5).sum())} de {len(conv)}.", "",
                "Temas mais fragmentados (n ≥ 300):\n",
                md(frag[frag["n"] >= 300].head(8)[["tema", "n", "n_topicos", "topicos_para_80pct", "entropia_norm", "maior_topico_pct"]]), "",
                "Tópicos menos puros (n ≥ 150):\n",
                md(conv[conv["n"] >= 150].head(8)[["topico", "nome", "n", "tema_dominante", "pureza", "temas_para_80pct"]]), ""]
    (a.saida / "relatorio_fase4.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"\nRelatório em {a.saida / 'relatorio_fase4.md'}")


if __name__ == "__main__":
    main()
