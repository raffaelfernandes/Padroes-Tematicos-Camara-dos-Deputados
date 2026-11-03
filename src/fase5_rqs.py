"""
fase5_rqs.py

Fase 5 do TCC: responde às perguntas de pesquisa com os tópicos da Fase 3.

RQ1. Que tópicos ganham peso nos meses que antecedem as eleições gerais?
     Janelas: abril a setembro de 2022 e de 2026 (eleições em 02/10/2022 e 04/10/2026).
     Métrica principal: fração dos deputados ativos na janela (com ao menos uma proposição)
     que apresentaram ao menos uma proposição do tópico. Cada deputado conta uma vez, então
     quem apresenta centenas de projetos não pesa mais que os outros.
     Métrica secundária: participação por volume (proposições do tópico / total da janela).
     Controle principal: os mesmos meses do ano anterior (2021 e 2025), com teste exato de
     Fisher e correção de Benjamini-Hochberg entre os tópicos.
     Controle de robustez: média dos mesmos meses nos anos sem eleição geral, sem 2020
     (2019, 2021, 2023, 2024, 2025), só como razão.
     Contraste secundário: eleição municipal de 2024 contra 2023.

RQ2. Os partidos têm assinaturas temáticas?
     Partido do primeiro autor na data da proposição (só deputados), grafia normalizada.
     Assinatura: log-odds com prior de Dirichlet informativo (Monroe, Colaresi e Quinn, 2008),
     partido contra o resto, em duas contagens: bruta e com peso limitado por deputado (cada
     proposição pesa min(1, C/n), com C = percentil 90 da produção por deputado), para que
     autores de produção em massa não definam o perfil do partido. Uma assinatura que vem de
     menos de 3 deputados ou de um deputado com mais de 50% das proposições do partido no
     tópico é marcada como individual. Separado por legislatura (56ª e 57ª).

Análise de sensibilidade (as duas RQs): todas as proposições; só o núcleo do HDBSCAN
(sem outliers reatribuídos nem formulaicas); sem os dois autores de produção em massa.

Uso (a partir de code/):
    uv run python src/fase5_rqs.py --base data/processed/base_fase2_20261101.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet

Saídas em data/processed/fase5/:
    relatorio_fase5.md                     resumo para leitura
    rq1_<versao>.csv                       um tópico por linha, as duas eleições e os controles
    rq1_serie_mensal_<versao>.csv          série mensal por tópico (deputados e volume), para as figuras
    rq2_<versao>_leg<56|57>.csv            partido x tópico, com log-odds e concentração
    rq2_concentracao.csv                   partido x ano: participação do maior autor
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path

import numpy as np
import pandas as pd

SAIDA = Path("data/processed/fase5")
COL = "topico_alt_ctfidf"                     # versão principal (formulaicas pelo c-TF-IDF)
MESES_JANELA = [4, 5, 6, 7, 8, 9]             # abril a setembro
ANOS_SEM_ELEICAO_GERAL = [2019, 2021, 2023, 2024, 2025]   # 2020 fica de fora (pandemia)
AUTORES_MASSA = ["Amom Mandel", "Duda Ramos"]  # G1: 2.348 proposições concentradas em dez/2025 e jul/2026
ALFA = 0.05
MIN_PROP_PARTIDO = 100                        # por legislatura
PRIOR_A0 = 500.0                              # força do prior de Dirichlet (em proposições)

# Grafia: mudanças de nome do mesmo partido viram uma sigla só
GRAFIA = {"REPUBLIC": "REPUBLICANOS", "PRB": "REPUBLICANOS", "PR": "PL", "PPS": "CIDADANIA",
          "PATRI": "PATRIOTA", "SOLIDARI": "SOLIDARIEDADE", "SOLIDARIED": "SOLIDARIEDADE"}
SEM_PARTIDO = {"S.PART.", "", None}


# ------------------------------------------------------------------ estatística sem scipy
def _lhyper(a, b, c, d):
    return (math.lgamma(a + b + 1) + math.lgamma(c + d + 1) + math.lgamma(a + c + 1) + math.lgamma(b + d + 1)
            - math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(c + 1) - math.lgamma(d + 1)
            - math.lgamma(a + b + c + d + 1))


def fisher_bilateral(a: int, b: int, c: int, d: int) -> float:
    """Teste exato de Fisher, bilateral, para a tabela [[a, b], [c, d]]."""
    r1, c1, n = a + b, a + c, a + b + c + d
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    obs = _lhyper(a, b, c, d)
    p = 0.0
    for x in range(lo, hi + 1):
        lp = _lhyper(x, r1 - x, c1 - x, n - r1 - c1 + x)
        if lp <= obs + 1e-7:
            p += math.exp(lp)
    return min(1.0, p)


def benjamini_hochberg(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float)
    ok = ~np.isnan(p)
    out = np.full_like(p, np.nan)
    q = p[ok]
    if not len(q):
        return out
    o = np.argsort(q)
    ajust = q[o] * len(q) / np.arange(1, len(q) + 1)
    ajust = np.minimum.accumulate(ajust[::-1])[::-1]
    r = np.empty_like(q)
    r[o] = np.minimum(ajust, 1.0)
    out[ok] = r
    return out


def log_odds_dirichlet(y_i: np.ndarray, y_j: np.ndarray, prior: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Monroe, Colaresi e Quinn (2008): log-odds do grupo i contra j com prior de Dirichlet
    informativo. Devolve (delta, z)."""
    a0, ni, nj = prior.sum(), y_i.sum(), y_j.sum()
    li = np.log((y_i + prior) / (ni + a0 - y_i - prior))
    lj = np.log((y_j + prior) / (nj + a0 - y_j - prior))
    delta = li - lj
    var = 1.0 / (y_i + prior) + 1.0 / (y_j + prior)
    return delta, delta / np.sqrt(var)


# ------------------------------------------------------------------ dados
def carregar(base_p: Path, topicos_p: Path) -> tuple[pd.DataFrame, dict]:
    cols = ["id", "dataApresentacao", "siglaTipo", "legislatura", "autor1_nome", "autor1_idDeputado",
            "autor1_partido", "autor1_eh_deputado", "eh_formulaica"]
    b = pd.read_parquet(base_p, columns=cols)
    t = pd.read_parquet(topicos_p)[["id", COL, "origem_topico"]]
    d = b.merge(t, on="id", validate="one_to_one")
    d = d[d["autor1_eh_deputado"] & d["autor1_idDeputado"].notna()].copy()
    d["data"] = pd.to_datetime(d["dataApresentacao"])
    d["ano"], d["mes"] = d["data"].dt.year, d["data"].dt.month
    d["ym"] = d["data"].dt.to_period("M").astype(str)
    d["dep"] = d["autor1_idDeputado"].astype("int64")
    d["topico"] = d[COL].astype(int)
    p = d["autor1_partido"].astype("string").str.strip().str.upper()
    p = p.replace({k.upper(): v for k, v in GRAFIA.items()})
    d["partido"] = p.mask(p.isin(list(SEM_PARTIDO - {None})) | p.isna())
    tag = topicos_p.stem.replace("topicos_", "")
    info = pd.read_csv(topicos_p.parent / f"topic_info_{tag}.csv")
    nomes = {int(r.Topic): ", ".join(ast.literal_eval(r.Representation)[:4]) for r in info.itertuples() if r.Topic >= 0}
    return d, nomes


def versoes(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    massa = d["autor1_nome"].isin(AUTORES_MASSA)
    return {
        "todas": d,
        "nucleo": d[d["origem_topico"] == "hdbscan"],
        "sem_massa": d[~massa],
    }


# ------------------------------------------------------------------ RQ1
def taxa_deputados(x: pd.DataFrame) -> tuple[pd.Series, int]:
    """Deputados distintos por tópico e deputados ativos no recorte."""
    ativos = x["dep"].nunique()
    por_top = x.groupby("topico")["dep"].nunique()
    return por_top, ativos


def recorte(d: pd.DataFrame, ano: int) -> pd.DataFrame:
    return d[(d["ano"] == ano) & d["mes"].isin(MESES_JANELA)]


def rq1(d: pd.DataFrame, nomes: dict) -> tuple[pd.DataFrame, dict]:
    tops = sorted(nomes)
    out = pd.DataFrame({"topico": tops, "nome": [nomes[t] for t in tops]}).set_index("topico")
    ativos = {}

    # Controle de robustez: média das taxas nos anos sem eleição geral
    taxas_base = []
    for a in ANOS_SEM_ELEICAO_GERAL:
        pt, at = taxa_deputados(recorte(d, a))
        taxas_base.append((pt.reindex(tops, fill_value=0) / at) if at else pd.Series(np.nan, index=tops))
    base_media = pd.concat(taxas_base, axis=1).mean(axis=1)

    for ano_el, ano_ct, rot in [(2022, 2021, "2022"), (2026, 2025, "2026"), (2024, 2023, "mun2024")]:
        J, C = recorte(d, ano_el), recorte(d, ano_ct)
        pj, aj = taxa_deputados(J)
        pc, ac = taxa_deputados(C)
        pj, pc = pj.reindex(tops, fill_value=0), pc.reindex(tops, fill_value=0)
        vj = J["topico"].value_counts().reindex(tops, fill_value=0) / max(len(J), 1)
        vc = C["topico"].value_counts().reindex(tops, fill_value=0) / max(len(C), 1)
        out[f"dep_{rot}"] = pj
        out[f"taxa_{rot}"] = (pj / aj).round(4)
        out[f"taxa_ctrl_{rot}"] = (pc / ac).round(4)
        out[f"razao_{rot}"] = ((pj / aj) / (pc / ac).replace(0, np.nan)).round(3)
        out[f"p_{rot}"] = [fisher_bilateral(int(pj[t]), int(aj - pj[t]), int(pc[t]), int(ac - pc[t])) for t in tops]
        out[f"p_aj_{rot}"] = benjamini_hochberg(out[f"p_{rot}"].to_numpy()).round(5)
        out[f"razao_volume_{rot}"] = (vj / vc.replace(0, np.nan)).round(3)
        if rot != "mun2024":
            out[f"razao_media_{rot}"] = ((pj / aj) / base_media.replace(0, np.nan)).round(3)
        ativos[rot] = (int(aj), int(ac))

    def sobe(rot):
        return (out[f"p_aj_{rot}"] < ALFA) & (out[f"razao_{rot}"] > 1)

    def cai(rot):
        return (out[f"p_aj_{rot}"] < ALFA) & (out[f"razao_{rot}"] < 1)

    out["padrao"] = np.select(
        [sobe("2022") & sobe("2026"), sobe("2022") & ~sobe("2026"), sobe("2026") & ~sobe("2022"),
         cai("2022") & cai("2026"), cai("2022") | cai("2026")],
        ["sobe nas duas", "sobe só em 2022", "sobe só em 2026", "cai nas duas", "cai em uma"], "estável")
    return out.reset_index(), ativos


def serie_mensal(d: pd.DataFrame, nomes: dict) -> pd.DataFrame:
    ativos = d.groupby("ym")["dep"].nunique().rename("ativos")
    total = d.groupby("ym").size().rename("total")
    s = d.groupby(["ym", "topico"]).agg(deputados=("dep", "nunique"), proposicoes=("id", "size")).reset_index()
    s = s.merge(ativos, on="ym").merge(total, on="ym")
    s["taxa_deputados"] = (s["deputados"] / s["ativos"]).round(4)
    s["participacao_volume"] = (s["proposicoes"] / s["total"]).round(4)
    s["nome"] = s["topico"].map(nomes)
    return s


# ------------------------------------------------------------------ RQ2
def p_normal(z: np.ndarray) -> np.ndarray:
    """p bilateral de um escore z."""
    return np.array([math.erfc(abs(v) / math.sqrt(2)) for v in z])


def rq2(d: pd.DataFrame, nomes: dict, leg: int) -> tuple[pd.DataFrame, float]:
    x = d[(d["legislatura"] == leg) & d["partido"].notna()].copy()
    tam = x["partido"].value_counts()
    partidos = sorted(tam[tam >= MIN_PROP_PARTIDO].index)
    tops = sorted(nomes)
    # Peso limitado por deputado: cada proposição pesa min(1, C / n_d), em que n_d é o número de
    # proposições do deputado no partido e na legislatura e C é o percentil 90 de n_d. Quem produz
    # em massa passa a valer C proposições; ninguém é inflado.
    n_d = x.groupby(["partido", "dep"])["id"].transform("size")
    C = float(np.percentile(x.groupby(["partido", "dep"]).size(), 90))
    x["peso"] = np.minimum(1.0, C / n_d)
    bruto = pd.crosstab(x["partido"], x["topico"]).reindex(columns=tops, fill_value=0)
    limit = x.pivot_table(index="partido", columns="topico", values="peso", aggfunc="sum", fill_value=0) \
             .reindex(columns=tops, fill_value=0)
    tot_b, tot_l = bruto.sum(0).to_numpy(float), limit.sum(0).to_numpy(float)
    prior_b = PRIOR_A0 * tot_b / tot_b.sum()
    prior_l = PRIOR_A0 * tot_l / tot_l.sum()
    blocos = []
    for p in partidos:
        y_b, y_l = bruto.loc[p].to_numpy(float), limit.loc[p].to_numpy(float)
        _, z_b = log_odds_dirichlet(y_b, tot_b - y_b, prior_b)
        _, z_l = log_odds_dirichlet(y_l, tot_l - y_l, prior_l)
        xp = x[x["partido"] == p]
        deps = xp.groupby("topico")["dep"].nunique()
        conc = xp.groupby(["topico", "autor1_nome"]).size().reset_index(name="n") \
                 .sort_values("n", ascending=False).drop_duplicates("topico").set_index("topico")
        r = pd.DataFrame({
            "legislatura": leg, "partido": p, "n_partido": int(tam[p]), "deputados_partido": int(xp["dep"].nunique()),
            "topico": tops, "nome": [nomes[t] for t in tops], "n": y_b.astype(int),
            "part_partido": (y_b / tam[p]).round(4), "part_geral": (tot_b / tot_b.sum()).round(4),
            "z_bruto": z_b.round(2), "z_limitado": z_l.round(2),
            "p_aj": benjamini_hochberg(p_normal(z_l)).round(4),
            "deputados_no_topico": deps.reindex(tops, fill_value=0).to_numpy(),
            "maior_autor": [conc.loc[t, "autor1_nome"] if t in conc.index else "" for t in tops],
            "maior_autor_pct": [round(conc.loc[t, "n"] / y_b[k], 3) if y_b[k] else np.nan for k, t in enumerate(tops)],
        })
        r["lift"] = (r["part_partido"] / r["part_geral"].replace(0, np.nan)).round(3)
        blocos.append(r)
    r = pd.concat(blocos, ignore_index=True)
    sig = (r["z_limitado"] > 0) & (r["p_aj"] < ALFA) & (r["z_bruto"] >= 1.96)
    coletiva = (r["deputados_no_topico"] >= 3) & (r["maior_autor_pct"] <= 0.5)
    r["assinatura"] = np.select([sig & coletiva, sig & ~coletiva], ["partidária", "individual"], "")
    return r, C


def concentracao(d: pd.DataFrame) -> pd.DataFrame:
    x = d[d["partido"].notna()]
    g = x.groupby(["partido", "ano", "autor1_nome"]).size().reset_index(name="n")
    tot = g.groupby(["partido", "ano"])["n"].transform("sum")
    g["pct"] = g["n"] / tot
    top = g.sort_values("pct", ascending=False).drop_duplicates(["partido", "ano"])
    tot_pa = x.groupby(["partido", "ano"]).size().rename("total_partido_ano")
    top = top.merge(tot_pa, on=["partido", "ano"]).rename(columns={"autor1_nome": "maior_autor", "n": "n_maior_autor"})
    top["acima_50pct"] = top["pct"] > 0.5
    return top[["partido", "ano", "total_partido_ano", "maior_autor", "n_maior_autor", "pct", "acima_50pct"]] \
        .sort_values(["partido", "ano"]).round({"pct": 3})


# ------------------------------------------------------------------ relatório
def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lin = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in df.itertuples(index=False):
        lin.append("| " + " | ".join(str(v).replace("|", "/") for v in r) + " |")
    return "\n".join(lin)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--topicos", required=True, type=Path)
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    d, nomes = carregar(a.base, a.topicos)
    print(f"{len(d)} proposições de deputados, {d['dep'].nunique()} deputados, {len(nomes)} tópicos")

    rel = ["# Fase 5: RQ1 e RQ2\n", f"Tópicos: `{a.topicos.name}`. Proposições de deputados: {len(d)}.\n"]
    res1, res2, ativos, limites = {}, {}, {}, {}
    for v, dv in versoes(d).items():
        r, ativos[v] = rq1(dv, nomes)
        r.to_csv(SAIDA / f"rq1_{v}.csv", index=False)
        serie_mensal(dv, nomes).to_csv(SAIDA / f"rq1_serie_mensal_{v}.csv", index=False)
        res1[v] = r
        for leg in (56, 57):
            r2, C = rq2(dv, nomes, leg)
            limites[(v, leg)] = C
            r2.to_csv(SAIDA / f"rq2_{v}_leg{leg}.csv", index=False)
            res2[(v, leg)] = r2
        print(f"[{v}] {len(dv)} proposições; RQ1: " + ", ".join(f"{k}: {n}" for k, n in r["padrao"].value_counts().items()))
    conc = concentracao(d)
    conc.to_csv(SAIDA / "rq2_concentracao.csv", index=False)

    # ---------- RQ1 no relatório
    p = res1["todas"]
    at22, at26 = ativos["todas"]["2022"], ativos["todas"]["2026"]
    rel += ["## RQ1: tópicos que ganham peso antes das eleições gerais\n",
            "Métrica: fração dos deputados ativos na janela (abril a setembro) que apresentaram ao menos uma "
            "proposição do tópico. Controle: mesmos meses do ano anterior. Teste exato de Fisher com correção de "
            f"Benjamini-Hochberg (α = {ALFA}). `razao_media`: contra a média dos anos sem eleição geral (sem 2020).\n",
            f"Deputados ativos (janela, controle): 2022 {at22}; 2026 {at26}.\n"]
    sens = pd.DataFrame({v: r.set_index("topico")["padrao"] for v, r in res1.items()})
    cols = ["topico", "nome", "taxa_ctrl_2022", "taxa_2022", "razao_2022", "p_aj_2022", "razao_media_2022",
            "taxa_ctrl_2026", "taxa_2026", "razao_2026", "p_aj_2026", "razao_media_2026", "padrao"]
    for titulo, filtro in [("Sobem nas duas eleições", "sobe nas duas"), ("Sobem só em 2022", "sobe só em 2022"),
                           ("Sobem só em 2026", "sobe só em 2026"), ("Caem nas duas", "cai nas duas")]:
        x = p[p["padrao"] == filtro].copy()
        if len(x):
            x["mantém_no_núcleo"] = x["topico"].map(sens["nucleo"]).eq(filtro)
            x["mantém_sem_massa"] = x["topico"].map(sens["sem_massa"]).eq(filtro)
            rel += [f"### {titulo} ({len(x)})\n", md(x[cols + ["mantém_no_núcleo", "mantém_sem_massa"]]), ""]
    rel += ["### Padrões por versão da análise de sensibilidade\n",
            md(pd.DataFrame({v: r["padrao"].value_counts() for v, r in res1.items()}).fillna(0).astype(int).reset_index()
               .rename(columns={"index": "padrão", "padrao": "padrão"})), ""]
    m = p.sort_values("razao_mun2024", ascending=False).head(8)
    rel += ["### Contraste: eleição municipal de 2024 contra 2023 (8 maiores razões)\n",
            md(m[["topico", "nome", "taxa_ctrl_mun2024", "taxa_mun2024", "razao_mun2024", "p_aj_mun2024"]]), ""]

    # ---------- RQ2 no relatório
    rel += ["## RQ2: assinaturas temáticas dos partidos\n",
            f"Partidos com pelo menos {MIN_PROP_PARTIDO} proposições na legislatura. Log-odds com prior de Dirichlet "
            f"(a0 = {PRIOR_A0:.0f}), partido contra o resto. `z_limitado`: cada proposição pesa min(1, C/n), em que n é a "
            f"produção do deputado no partido e C o percentil 90 dessa produção (C = {limites[('todas', 56)]:.0f} na 56ª e "
            f"{limites[('todas', 57)]:.0f} na 57ª). Assinatura = z_limitado positivo com p ajustado (BH, por partido) "
            f"abaixo de {ALFA} e z_bruto ≥ 1,96. `partidária`: pelo menos 3 deputados no tópico e nenhum com mais de 50%; "
            "senão `individual`.\n"]
    for leg in (56, 57):
        r2 = res2[("todas", leg)]
        nuc = res2[("nucleo", leg)].set_index(["partido", "topico"])["z_limitado"]
        top = (r2.sort_values("z_limitado", ascending=False).groupby("partido").head(3)
                 .sort_values(["partido", "z_limitado"], ascending=[True, False]))
        top = top.assign(z_nucleo=[nuc.get((pp, tt), np.nan) for pp, tt in zip(top["partido"], top["topico"])])
        rel += [f"### {leg}ª legislatura: três tópicos mais característicos de cada partido\n",
                md(top[["partido", "n_partido", "deputados_partido", "topico", "nome", "n", "lift", "z_bruto",
                        "z_limitado", "z_nucleo", "deputados_no_topico", "maior_autor", "maior_autor_pct", "assinatura"]]), ""]
        cont = r2[r2["assinatura"] != ""].groupby(["partido", "assinatura"]).size().unstack(fill_value=0)
        rel += [f"Assinaturas por partido na {leg}ª legislatura:\n", md(cont.reset_index()), ""]
    alto = conc[conc["acima_50pct"] & (conc["total_partido_ano"] >= 50)]
    rel += ["### Partido e ano em que um deputado passa de 50% das proposições do partido\n",
            md(alto) if len(alto) else "Nenhum.", ""]
    (SAIDA / "relatorio_fase5.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {SAIDA / 'relatorio_fase5.md'}")


if __name__ == "__main__":
    main()
