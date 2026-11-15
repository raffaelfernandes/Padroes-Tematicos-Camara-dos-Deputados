"""
comparar_modelos.py

Compara os tópicos dos três modelos de embedding (BERTimbau Large, Serafim 335M e
multilingual-e5-large) nas análises que, no texto, foram feitas com o BERTimbau:
  1. concordância entre as partições dos modelos (ARI, NMI e correspondência de tópicos);
  2. fragmentação dos temas oficiais;
  3. pares de temas que o modelo aproxima ou separa em relação ao CEDI (razão sobre o acaso);
  4. assinaturas partidárias (mesmo procedimento da Fase 5, versão com todas as proposições).

Rodar a partir de code/:
    uv run python src/extras/comparar_modelos.py
Saídas em data/processed/fase4/comparacao_modelos/ (CSVs e relatorio.md).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

sys.path.insert(0, "src")
import fase5_rqs as f5  # noqa: E402
from fase5_figuras import ROTULOS  # noqa: E402

P = Path("data/processed")
SAIDA = P / "fase4" / "comparacao_modelos"
COL = "topico_alt_ctfidf"
MODELOS = {
    "BERTimbau": "bertimbau_nn30_mcs100_eom_ms10_rk",
    "Serafim": "serafim_nn30_mcs100_eom_ms5_rk",
    "e5": "e5_nn30_mcs100_eom_ms10_rk",
}
BASE = sorted(P.glob("base_fase2_*.parquet"))[-1]
TEMAS = P / "temas_long_20261027.parquet"
PARES_TEXTO = [  # os seis pares da Tabela de pares do texto
    ("Direito Penal e Processual Penal", "Direito e Justiça"),
    ("Direito Penal e Processual Penal", "Direitos Humanos e Minorias"),
    ("Saúde", "Trabalho e Emprego"),
    ("Economia", "Relações Internacionais e Comércio Exterior"),
    ("Estrutura Fundiária", "Agricultura, Pecuária, Pesca e Extrativismo"),
    ("Economia", "Turismo"),
    ("Arte, Cultura e Religião", "Turismo"),
]
TEMAS_FRAG = ["Administração Pública", "Direitos Humanos e Minorias", "Indústria, Comércio e Serviços",
              "Finanças Públicas e Orçamento", "Direito Penal e Processual Penal",
              "Homenagens e Datas Comemorativas", "Política, Partidos e Eleições"]


def md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) if len(df) else "(vazio)"


def termos(tag: str) -> dict[int, str]:
    info = pd.read_csv(P / f"fase3/topic_info_{tag}.csv")
    return {int(r.Topic): ", ".join(ast.literal_eval(r.Representation)[:4]) for r in info.itertuples() if r.Topic >= 0}


def pares_de_temas(dt: pd.DataFrame, nome_tema: dict) -> pd.DataFrame:
    """Mesma conta do exportar_painel.py: razão sobre o acaso no CEDI e no modelo."""
    N = len(dt)
    longo = dt[["id", "topico", "temas"]].explode("temas").reset_index(drop=True)
    Mt = pd.crosstab(longo["topico"], longo["temas"])
    cods = list(Mt.columns)
    Na = Mt.sum(axis=0).to_numpy(float)
    idx = {c: i for i, c in enumerate(cods)}
    TT = np.zeros((len(cods), len(cods)))
    for s in dt["temas"]:
        l = [idx[c] for c in s]
        for i in l:
            for j in l:
                TT[i, j] += 1
    mm = Mt.to_numpy(float)
    S2 = float(((dt["topico"].value_counts() / N) ** 2).sum())
    co = mm.T @ mm
    out = []
    for i in range(len(cods)):
        for j in range(i + 1, len(cods)):
            if Na[i] < 300 or Na[j] < 300:
                continue
            nab = TT[i, j]
            out.append({"tema_a": nome_tema[int(cods[i])], "tema_b": nome_tema[int(cods[j])],
                        "lift_cedi": nab * N / (Na[i] * Na[j]),
                        "lift_modelo": (co[i, j] - nab) / ((Na[i] * Na[j] - nab) * S2)})
    return pd.DataFrame(out)


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    temas = pd.read_parquet(TEMAS)
    nome_tema = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    tops = {m: pd.read_parquet(P / f"fase3/topicos_{tag}.parquet")[["id", COL, "origem_topico"]]
            .rename(columns={COL: "topico"}) for m, tag in MODELOS.items()}
    ids = sorted(set.intersection(*[set(t["id"]) for t in tops.values()]))
    lab = {m: t.set_index("id").loc[ids, "topico"].to_numpy() for m, t in tops.items()}
    rel = ["# Comparação entre os três modelos\n",
           f"Proposições em comum: {len(ids)}. Coluna de tópico: `{COL}` (formulaicas pelo c-TF-IDF).\n"]

    # ---------------- 1. concordância entre partições
    linhas, corr = [], []
    nomes = list(MODELOS)
    for a in range(len(nomes)):
        for b in range(a + 1, len(nomes)):
            ma, mb = nomes[a], nomes[b]
            ct = pd.crosstab(lab[ma], lab[mb])
            na, nb = ct.sum(1).to_numpy(), ct.sum(0).to_numpy()
            inter = ct.to_numpy()
            jac = inter / (na[:, None] + nb[None, :] - inter)
            melhor_a = jac.max(1)          # para cada tópico de ma, o tópico mais parecido de mb
            melhor_b = jac.max(0)
            linhas.append({"modelo_a": ma, "modelo_b": mb,
                           "ARI": adjusted_rand_score(lab[ma], lab[mb]),
                           "NMI": normalized_mutual_info_score(lab[ma], lab[mb]),
                           "topicos_a_com_par_jac50": float((melhor_a >= 0.5).mean()),
                           "topicos_b_com_par_jac50": float((melhor_b >= 0.5).mean()),
                           "jaccard_mediano_a": float(np.median(melhor_a)),
                           "jaccard_mediano_b": float(np.median(melhor_b))})
            if ma == "BERTimbau":
                corr.append(pd.DataFrame({"topico_bertimbau": ct.index, f"jaccard_{mb}": melhor_a.round(3),
                                          f"par_{mb}": ct.columns[jac.argmax(1)]}).set_index("topico_bertimbau"))
    acaso = []
    rng = np.random.default_rng(130)
    for _ in range(5):
        acaso.append(adjusted_rand_score(lab["BERTimbau"], rng.permutation(lab["e5"])))
    conc = pd.DataFrame(linhas).round(3)
    conc.to_csv(SAIDA / "concordancia_particoes.csv", index=False)
    pd.concat(corr, axis=1).reset_index().to_csv(SAIDA / "correspondencia_topicos_bertimbau.csv", index=False)
    rel += ["## 1. Concordância entre as partições\n",
            "ARI e NMI entre os tópicos de cada par de modelos; `topicos_a_com_par_jac50`: fração dos tópicos do "
            "modelo A cujo tópico mais parecido no modelo B tem Jaccard de pelo menos 0,5.\n",
            md(conc), f"\nARI com o e5 embaralhado (5 sementes): média {np.mean(acaso):.4f}.\n"]

    # ---------------- 2 e 3. fragmentação e pares de temas
    frag, pares = {}, {}
    for m, tag in MODELOS.items():
        dt = tops[m].assign(temas=lambda x: x["id"].map(conj)).dropna(subset=["temas"]).reset_index(drop=True)
        # fragmentação: nº de tópicos para reunir 80% das proposições do tema (mesma coluna de tópico do texto)
        lg = dt[["topico", "temas"]].explode("temas").reset_index(drop=True)
        lg["tema"] = lg["temas"].astype(int).map(nome_tema)
        frag[m] = lg.groupby("tema")["topico"].apply(
            lambda s: int((s.value_counts(normalize=True).cumsum() < 0.8).sum() + 1))
        pares[m] = pares_de_temas(dt, nome_tema)
    ntop = {m: tops[m]["topico"].nunique() for m in MODELOS}
    fr = pd.DataFrame(frag).loc[TEMAS_FRAG].reset_index()
    fr.columns = ["tema"] + [f"{m} ({ntop[m]} tópicos)" for m in MODELOS]
    fr_all = pd.DataFrame(frag)
    sp = fr_all.rank().corr(method="pearson").round(3)
    fr.to_csv(SAIDA / "fragmentacao.csv", index=False)
    rel += ["## 2. Fragmentação (tópicos para reunir 80% do tema)\n", md(fr),
            "\nCorrelação de Spearman da fragmentação entre os modelos (todos os temas):\n", md(sp.reset_index()), ""]

    base_p = pares["BERTimbau"][["tema_a", "tema_b", "lift_cedi"]].copy()
    for m in MODELOS:
        base_p[m] = pares[m]["lift_modelo"].to_numpy()
    base_p.to_csv(SAIDA / "pares_de_temas.csv", index=False)
    sel = []
    for a, b in PARES_TEXTO:
        r = base_p[((base_p.tema_a == a) & (base_p.tema_b == b)) | ((base_p.tema_a == b) & (base_p.tema_b == a))]
        sel.append(r)
    sel = pd.concat(sel).round(2)
    # sentido da divergência: o modelo aproxima (lift_modelo > lift_cedi) ou separa
    sentido = pd.DataFrame({m: np.sign(base_p[m] - base_p["lift_cedi"]) for m in MODELOS})
    acordo = {f"{a} x {b}": float((sentido[a] == sentido[b]).mean())
              for i, a in enumerate(MODELOS) for b in list(MODELOS)[i + 1:]}
    log_corr = np.log(base_p[list(MODELOS)].clip(lower=1e-3)).corr().round(3)
    rel += ["## 3. Pares de temas (razão sobre o acaso)\n", md(sel),
            f"\nPares com pelo menos 300 proposições em cada tema: {len(base_p)}.\n",
            "Fração dos pares em que dois modelos divergem do CEDI no mesmo sentido (ambos aproximam ou ambos separam):\n",
            md(pd.DataFrame([acordo]).round(3)),
            "\nCorrelação (Pearson, log da razão) entre os modelos:\n", md(log_corr.reset_index()), ""]

    # ---------------- 4. assinaturas partidárias
    rel += ["## 4. Assinaturas partidárias (versão com todas as proposições)\n"]
    sig = {}
    for m, tag in MODELOS.items():
        d, nomes_t = f5.carregar(BASE, P / f"fase3/topicos_{tag}.parquet")
        rot = ROTULOS if m == "BERTimbau" else nomes_t
        for leg in (56, 57):
            r, _ = f5.rq2(d, nomes_t, leg)
            r["rotulo"] = r["topico"].map(lambda t: rot.get(t, nomes_t.get(t, "")))
            r["modelo"] = m
            sig[(m, leg)] = r
            r.to_csv(SAIDA / f"rq2_{m}_leg{leg}.csv", index=False)
    resumo = []
    for leg in (56, 57):
        for m in MODELOS:
            r = sig[(m, leg)]
            part = r[r["assinatura"] == "partidária"]
            resumo.append({"legislatura": leg, "modelo": m, "partidos": r["partido"].nunique(),
                           "partidos_com_assinatura": part["partido"].nunique(),
                           "assinaturas_partidarias": len(part)})
    rel += [md(pd.DataFrame(resumo)), ""]

    # correspondência: assinatura do BERTimbau (partido, tópico) reaparece no outro modelo se o tópico
    # correspondente (maior interseção) também é assinatura partidária do mesmo partido
    ct_map = {}
    for m in ("Serafim", "e5"):
        ct = pd.crosstab(lab["BERTimbau"], lab[m])
        ct_map[m] = ct
    rep = []
    for leg in (56, 57):
        b = sig[("BERTimbau", leg)]
        b = b[b["assinatura"] == "partidária"]
        for m in ("Serafim", "e5"):
            o = sig[(m, leg)]
            o_set = set(zip(o.loc[o["assinatura"] == "partidária", "partido"], o.loc[o["assinatura"] == "partidária", "topico"]))
            o_any = set(zip(o.loc[o["assinatura"] != "", "partido"], o.loc[o["assinatura"] != "", "topico"]))
            ct = ct_map[m]
            achou, achou_qq = 0, 0
            for p, t in zip(b["partido"], b["topico"]):
                # tópicos do outro modelo que recebem pelo menos 20% das proposições do tópico t
                linha = ct.loc[t] / ct.loc[t].sum()
                cand = set(linha[linha >= 0.2].index)
                achou += any((p, c) in o_set for c in cand)
                achou_qq += any((p, c) in o_any for c in cand)
            rep.append({"legislatura": leg, "modelo": m, "assinaturas_bertimbau": len(b),
                        "reaparecem_partidarias": achou, "reaparecem_qualquer": achou_qq})
    rep = pd.DataFrame(rep)
    rep.to_csv(SAIDA / "assinaturas_reaparecem.csv", index=False)
    rel += ["Assinaturas partidárias do BERTimbau que reaparecem no outro modelo (mesmo partido, em um tópico que "
            "recebe pelo menos 20% das proposições do tópico do BERTimbau):\n", md(rep), ""]
    for leg in (56, 57):
        for m in MODELOS:
            r = sig[(m, leg)]
            part = r[r["assinatura"] == "partidária"].sort_values(["partido", "z_limitado"], ascending=[True, False])
            lista = part.groupby("partido")["rotulo"].apply(lambda s: "; ".join(s)).reset_index()
            rel += [f"### {leg}ª legislatura, {m}\n", md(lista), ""]
    (SAIDA / "relatorio.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {SAIDA / 'relatorio.md'}")


if __name__ == "__main__":
    main()
