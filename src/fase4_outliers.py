"""
fase4_outliers.py

Análise dos outliers do HDBSCAN (proposições que o modelo não colocou em nenhum tópico e que
o reduce_outliers reatribuiu depois). Três partes:

  metricas   parte quantitativa, sem anotação:
               - perfil dos outliers (nº de temas oficiais, tipo, ano, tema oficial);
               - qualidade da reatribuição: concordância temática com o núcleo do tópico
                 (P_nucleo) para membros do núcleo, outliers reatribuídos, formulaicas e
                 outliers jogados num tópico aleatório; e por faixa de similaridade.
  amostrar   sorteia uma amostra aleatória de outliers e gera a planilha de anotação.
  resumir    lê a planilha anotada e calcula proporções com intervalo de confiança
             (Wilson, 95%) e, se houver um segundo anotador, o kappa de Cohen.

P_nucleo(e) = fração dos membros do núcleo (atribuídos pelo próprio HDBSCAN) do tópico de e
que compartilham ao menos um tema oficial com e. Para os membros do núcleo, e é excluído do
próprio cálculo. É a precisão do BCubed calculada só contra o núcleo.

Uso (a partir de code/):
    uv run python src/fase4_outliers.py metricas --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10.parquet
    uv run python src/fase4_outliers.py amostrar --base ... --temas ... --topicos ... --n 100
    uv run python src/fase4_outliers.py resumir --anotada anotacoes/outliers_analise_erros.csv [--anotada2 anotacoes/outliers_analise_erros_2.csv]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fase4_avaliacao import Gabarito, md as tabela_md  # noqa: E402

SEED = 130
SAIDA = Path("data/processed/fase4")
ANOT = Path("anotacoes")          # anotações humanas ficam versionadas, como as das formulaicas

CODIGOS_MOTIVO = {
    "H": "híbrida: mistura assuntos que estariam em tópicos diferentes",
    "N": "nicho: assunto específico e claro, sem tópico próprio",
    "G": "genérica: ementa ampla ou vaga, assunto difícil de definir",
    "B": "borda: o assunto é claramente de um tópico existente",
    "O": "outro (explicar em obs)",
}
CODIGOS_REATRIB = {
    "A": "adequada: o tópico atribuído descreve o assunto principal",
    "P": "parcial: descreve só uma parte do assunto ou um assunto vizinho",
    "I": "inadequada: o tópico não tem relação com o assunto",
}


# ---------------------------------------------------------------- carregamento
def carregar(base_p: Path, temas_p: Path, topicos_p: Path):
    base = pd.read_parquet(base_p, columns=["id", "siglaTipo", "ano", "ementa", "texto_modelo", "fonte_texto",
                                            "id_texto_unico", "eh_formulaica", "autor1_nome"])
    temas = pd.read_parquet(temas_p)
    nome_tema = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    t = pd.read_parquet(topicos_p).drop(columns=["id_texto_unico"])
    d = base.merge(t, on="id", validate="one_to_one")
    d = d[d["id"].isin(conj.index)].reset_index(drop=True)
    d["temas"] = d["id"].map(conj)
    tag = topicos_p.stem.replace("topicos_", "")
    modelo = tag.split("_")[0]
    emb = np.load(Path("data/processed/embeddings") / f"emb_{modelo}.npy", mmap_mode="r")
    E = np.asarray(emb[d["id_texto_unico"].to_numpy()], dtype=np.float32)
    info = pd.read_csv(topicos_p.parent / f"topic_info_{tag}.csv")
    return d, E, nome_tema, info, tag


class Nucleo:
    """Contagens de temas e centroides do núcleo (origem hdbscan) de cada tópico."""

    def __init__(self, d: pd.DataFrame, E: np.ndarray, col: str = "topico_alt_ctfidf"):
        self.gab = Gabarito(list(d["temas"]))
        self.top = d[col].to_numpy()
        self.org = d["origem_topico"].to_numpy()
        self.nuc = self.org == "hdbscan"
        self.T = int(self.top.max()) + 1
        sig = self.gab.sig
        C = np.zeros((self.T, self.gab.n_sig), np.float32)
        np.add.at(C, (self.top[self.nuc], sig[self.nuc]), 1)
        self.n_nuc = C.sum(1)
        self.A = C @ self.gab.comp.T
        cent = np.zeros((self.T, E.shape[1]), np.float32)
        np.add.at(cent, self.top[self.nuc], E[self.nuc])
        self.cent = cent / np.maximum(np.linalg.norm(cent, axis=1, keepdims=True), 1e-9)

    def p_nucleo(self, topicos: np.ndarray, idx: np.ndarray) -> np.ndarray:
        auto = self.nuc[idx] & (topicos == self.top[idx])
        num = self.A[topicos, self.gab.sig[idx]] - auto
        den = self.n_nuc[topicos] - auto
        return np.where(den > 0, num / np.maximum(den, 1), np.nan)


# ---------------------------------------------------------------- metricas
def metricas(a) -> None:
    d, E, nome_tema, info, tag = carregar(a.base, a.temas, a.topicos)
    nu = Nucleo(d, E)
    todos = np.arange(len(d))
    P = nu.p_nucleo(nu.top, todos)
    out = nu.org == "reduce_outliers"
    idx_out = np.nonzero(out)[0]
    rng = np.random.default_rng(SEED)
    prob = nu.n_nuc / nu.n_nuc.sum()
    P_aleat = float(np.mean([np.nanmean(nu.p_nucleo(rng.choice(nu.T, len(idx_out), p=prob), idx_out))
                             for _ in range(5)]))
    S = E[idx_out] @ nu.cent.T
    alt = S.argmax(1)
    P_orig = float(np.nanmean(nu.p_nucleo(alt, idx_out)))
    sim_atrib = S[np.arange(len(idx_out)), nu.top[idx_out]]

    rot = {"hdbscan": "núcleo do tópico (HDBSCAN)", "reduce_outliers": "outliers reatribuídos",
           "formulaica_centroide": "formulaicas"}
    linhas = [{"grupo": rot[o], "n": int((nu.org == o).sum()), "P_nucleo": round(float(np.nanmean(P[nu.org == o])), 3)}
              for o in rot]
    linhas.append({"grupo": "outliers num tópico aleatório (5 sementes)", "n": int(out.sum()), "P_nucleo": round(P_aleat, 3)})
    linhas.append({"grupo": "outliers pelo centroide no espaço original", "n": int(out.sum()), "P_nucleo": round(P_orig, 3)})
    qual = pd.DataFrame(linhas)

    sim_atrib = sim_atrib.astype(float)
    faixas = pd.qcut(sim_atrib, 5, labels=["Q1 (menor)", "Q2", "Q3", "Q4", "Q5 (maior)"])
    por_sim = (pd.DataFrame({"faixa": faixas, "sim": sim_atrib, "P": P[idx_out]})
                 .groupby("faixa", observed=True).agg(n=("P", "size"), sim_min=("sim", "min"),
                                                       sim_max=("sim", "max"), P_nucleo=("P", "mean")).round(3).reset_index())

    # Perfil
    d["outlier"] = out
    d["n_temas"] = d["temas"].map(len).clip(upper=4).map({1: "1", 2: "2", 3: "3", 4: "4 ou mais"})
    sub = d[~d["eh_formulaica"]]
    def perfil(col):
        g = sub.groupby(col)["outlier"].agg(n="size", pct_outliers="mean").reset_index()
        g["pct_outliers"] = (g["pct_outliers"] * 100).round(1)
        return g
    ex = sub[["outlier", "temas"]].explode("temas")
    ex["tema"] = ex["temas"].map(nome_tema)
    p_tema = (ex.groupby("tema")["outlier"].agg(n="size", pct_outliers="mean").reset_index()
                .query("n >= 200").sort_values("pct_outliers", ascending=False))
    p_tema["pct_outliers"] = (p_tema["pct_outliers"] * 100).round(1)

    SAIDA.mkdir(parents=True, exist_ok=True)
    qual.to_csv(SAIDA / f"outliers_reatribuicao_{tag}.csv", index=False)
    por_sim.to_csv(SAIDA / f"outliers_por_similaridade_{tag}.csv", index=False)
    for nome, g in [("n_temas", perfil("n_temas")), ("tipo", perfil("siglaTipo")), ("ano", perfil("ano")), ("tema", p_tema)]:
        g.to_csv(SAIDA / f"outliers_perfil_{nome}_{tag}.csv", index=False)

    md = [f"# Outliers: {tag}\n",
          f"Outliers entre as substantivas: {sub['outlier'].mean():.1%} ({int(sub['outlier'].sum())} de {len(sub)}).\n",
          "## Qualidade da reatribuição\n",
          "P_nucleo: fração do núcleo do tópico que compartilha ao menos um tema oficial com a proposição.\n",
          tabela_md(qual), "\n\n### Outliers por faixa de similaridade com o tópico atribuído\n",
          tabela_md(por_sim),
          "\n\n## Perfil\n", "### Por nº de temas oficiais\n", tabela_md(perfil("n_temas")),
          "\n\n### Por tipo\n", tabela_md(perfil("siglaTipo")),
          "\n\n### Por ano\n", tabela_md(perfil("ano")),
          "\n\n### Por tema oficial (temas com 200+ proposições)\n", tabela_md(p_tema), "\n"]
    (SAIDA / f"outliers_{tag}.md").write_text("\n".join(md), encoding="utf-8")
    print(qual.to_string(index=False)); print(); print(por_sim.to_string(index=False))
    print(f"\nRelatório: {SAIDA / f'outliers_{tag}.md'}")


# ---------------------------------------------------------------- amostrar
def amostrar(a) -> None:
    d, E, nome_tema, info, tag = carregar(a.base, a.temas, a.topicos)
    nu = Nucleo(d, E)
    idx_out = np.nonzero(nu.org == "reduce_outliers")[0]
    rng = np.random.default_rng(SEED)
    am = np.sort(rng.choice(idx_out, size=a.n, replace=False))
    S = E[am] @ nu.cent.T
    atrib = nu.top[am]
    S2 = S.copy(); S2[np.arange(len(am)), atrib] = -np.inf
    seg = S2.argmax(1)

    nomes = info.set_index("Topic")
    def descreve(t):
        termos = ", ".join(eval(nomes.loc[t, "Representation"])[:6])
        docs = eval(nomes.loc[t, "Representative_Docs"])[:2]
        return termos, " | ".join(x[:160] for x in docs)

    linhas, oculto = [], []
    for k, (i, t, t2) in enumerate(zip(am, atrib, seg), 1):
        r = d.iloc[i]
        termos, exemplos = descreve(t)
        termos2, _ = descreve(t2)
        texto = r["ementa"] if r["fonte_texto"] == "ementa" else f"{r['ementa']}  [texto usado: {str(r['texto_modelo'])[:300]}]"
        linhas.append({"n": k, "id": r["id"], "tipo": r["siglaTipo"], "texto": texto,
                       "topico_atribuido": f"{t}: {termos}", "exemplos_do_topico": exemplos,
                       "outro_topico_proximo": f"{t2}: {termos2}",
                       "motivo": "", "reatribuicao": "", "outro_seria_melhor": "", "obs": ""})
        oculto.append({"n": k, "id": r["id"], "temas_oficiais": "; ".join(sorted(nome_tema[x] for x in r["temas"])),
                       "n_temas": len(r["temas"]), "sim_atribuido": round(float(S[k - 1, t]), 3),
                       "sim_outro": round(float(S[k - 1, t2]), 3),
                       "P_nucleo": round(float(nu.p_nucleo(np.array([t]), np.array([i]))[0]), 3)})
    ANOT.mkdir(parents=True, exist_ok=True)
    dest = ANOT / "outliers_analise_erros.csv"
    if dest.exists() and not a.refazer:
        raise SystemExit(f"{dest} já existe (use --refazer para sobrescrever; cuidado com a anotação feita)")
    pd.DataFrame(linhas).to_csv(dest, index=False, encoding="utf-8-sig")
    pd.DataFrame(oculto).to_csv(ANOT / "outliers_analise_erros_OCULTO.csv", index=False, encoding="utf-8-sig")
    (ANOT / "outliers_analise_erros_codigos.json").write_text(json.dumps({"motivo": CODIGOS_MOTIVO, "reatribuicao": CODIGOS_REATRIB,
        "outro_seria_melhor": {"S": "sim", "N": "não"}, "modelo": tag, "seed": SEED, "n": a.n},
        indent=2, ensure_ascii=False), encoding="utf-8")
    cat = [f"# Catálogo de tópicos ({tag})\n",
           "Apoio à anotação: para decidir entre N (não existe tópico para o assunto) e B (existe), "
           "procure as palavras da finalidade nos termos E nos exemplos.\n"]
    for t in info[info["Topic"] >= 0].sort_values("Topic").itertuples():
        cat += [f"## {t.Topic} ({t.Count} proposições)", "**Termos:** " + ", ".join(eval(t.Representation)[:10]), ""]
        cat += [f"- {x[:220]}" for x in eval(t.Representative_Docs)[:3]] + [""]
    (ANOT / "outliers_analise_erros_catalogo_topicos.md").write_text("\n".join(cat), encoding="utf-8")
    print(f"{a.n} outliers sorteados (seed {SEED}) de {len(idx_out)}. Planilha: {dest}")
    print("Não abra o arquivo _OCULTO antes de terminar a anotação.")


# ---------------------------------------------------------------- resumir
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - m, c + m)


def kappa(x: pd.Series, y: pd.Series) -> float:
    cats = sorted(set(x) | set(y)); po = float((x == y).mean())
    pe = sum((x == c).mean() * (y == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def resumir(a) -> None:
    an = pd.read_csv(a.anotada, encoding="utf-8-sig")
    oc = pd.read_csv(a.anotada.with_name(a.anotada.stem + "_OCULTO.csv"), encoding="utf-8-sig")
    for c in ("motivo", "reatribuicao", "outro_seria_melhor"):
        an[c] = an[c].astype(str).str.strip().str.upper().str[:1]
    d = an.merge(oc, on=["n", "id"])
    md = [f"# Anotação dos outliers ({len(d)} proposições)\n"]
    for c, cod in [("motivo", CODIGOS_MOTIVO), ("reatribuicao", CODIGOS_REATRIB)]:
        vc = d[c].value_counts()
        tab = pd.DataFrame([{"código": k, "descrição": cod.get(k, "?"), "n": int(vc.get(k, 0)),
                             "%": round(100 * vc.get(k, 0) / len(d), 1),
                             "IC 95%": "{:.0f}% a {:.0f}%".format(*[100 * v for v in wilson(int(vc.get(k, 0)), len(d))])}
                            for k in cod])
        md += [f"## {c}\n", tabela_md(tab), "\n"]
        print(tab.to_string(index=False)); print()
    d["faixa_sim"] = pd.qcut(d["sim_atribuido"], 3, labels=["baixa", "média", "alta"])
    for col in ("n_temas", "faixa_sim", "motivo"):
        ct = pd.crosstab(d[col], d["reatribuicao"], normalize="index").mul(100).round(0)
        md += [f"### Reatribuição por {col} (% da linha)\n", tabela_md(ct, index=True), "\n"]
    s = d["outro_seria_melhor"].eq("S")
    md.append(f"Outro tópico próximo seria melhor: {s.sum()} de {len(d)} ({s.mean():.0%}).\n")
    if a.anotada2:
        b = pd.read_csv(a.anotada2, encoding="utf-8-sig")
        m = an.merge(b, on="n", suffixes=("_1", "_2"))
        for c in ("motivo", "reatribuicao"):
            x = m[f"{c}_1"]; y = m[f"{c}_2"].astype(str).str.strip().str.upper().str[:1]
            md.append(f"Concordância em {c} ({len(m)} itens): {(x == y).mean():.0%}, kappa de Cohen = {kappa(x, y):.2f}\n")
    dest = SAIDA / "outliers_anotacao_resumo.md"
    dest.write_text("\n".join(md), encoding="utf-8")
    print(f"Resumo: {dest}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("metricas", "amostrar"):
        s = sub.add_parser(nome)
        s.add_argument("--base", required=True, type=Path)
        s.add_argument("--temas", required=True, type=Path)
        s.add_argument("--topicos", required=True, type=Path)
    sub.choices["amostrar"].add_argument("--n", type=int, default=100)
    sub.choices["amostrar"].add_argument("--refazer", action="store_true")
    r = sub.add_parser("resumir")
    r.add_argument("--anotada", required=True, type=Path)
    r.add_argument("--anotada2", type=Path, default=None)
    a = ap.parse_args()
    {"metricas": metricas, "amostrar": amostrar, "resumir": resumir}[a.cmd](a)


if __name__ == "__main__":
    main()
