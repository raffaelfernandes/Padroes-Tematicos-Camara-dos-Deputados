"""
fase1_investigacoes.py

Checagens que precisam ser feitas antes de fechar o portão G1 e começar a
modelagem. Lê as saídas do montar_base_proposicoes.py.

Uso:
    uv run python src/fase1_investigacoes.py --base data/processed/base_proposicoes_20261027.parquet \
                                      --temas data/processed/temas_long_20261027.parquet

Saídas (em --saida, padrão data/processed/investigacoes):
    investigacoes_g1.md            relatório com as 7 investigações
    amostra_formulaicas.csv        candidatas a formulaica para você anotar
    duplicatas_discordantes.csv    ementas idênticas com temas oficiais diferentes
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# BCubed estendido (Amigó et al., 2009) para agrupamento rígido x gabarito
# multirrótulo. Com um cluster por item, |C(e) ∩ C(e')| vale 0 ou 1, então:
#   P(e,e') = 1 se e' está no mesmo cluster e compartilha ao menos um tema
#   R(e,e') = 1 / |L(e) ∩ L(e')| se e' está no mesmo cluster, senão 0
# A conta é feita por "assinatura" (conjunto de temas), não par a par,
# o que torna viável rodar em 40 mil itens.
# --------------------------------------------------------------------------

def bcubed_estendido(clusters: np.ndarray, rotulos: list[frozenset]) -> dict:
    df = pd.DataFrame({"c": clusters, "s": rotulos})
    df = df[df["s"].map(len) > 0]
    assin = sorted(set(df["s"]), key=lambda s: tuple(sorted(s)))
    idx = {s: i for i, s in enumerate(assin)}
    todos = sorted(set().union(*assin))
    col = {t: j for j, t in enumerate(todos)}
    M = np.zeros((len(assin), len(todos)), dtype=np.float32)
    for s, i in idx.items():
        for t in s:
            M[i, col[t]] = 1
    O = M @ M.T                       # |L ∩ L'| entre assinaturas
    comp = O > 0
    inv = np.where(comp, 1.0 / np.maximum(O, 1), 0.0)

    df["i"] = df["s"].map(idx)
    glob = np.bincount(df["i"], minlength=len(assin)).astype(np.float64)
    denom_r = comp @ glob             # nº de itens que compartilham tema com e (corpus todo)

    P_tot = R_tot = 0.0
    for _, g in df.groupby("c"):
        cnt = np.bincount(g["i"], minlength=len(assin)).astype(np.float64)
        presentes = np.nonzero(cnt)[0]
        p_num = comp[presentes] @ cnt
        r_num = inv[presentes] @ cnt
        P_tot += float((cnt[presentes] * p_num / len(g)).sum())
        R_tot += float((cnt[presentes] * r_num / denom_r[presentes]).sum())
    n = len(df)
    P, R = P_tot / n, R_tot / n
    return {"P": P, "R": R, "F": 2 * P * R / (P + R) if P + R else 0.0, "n": n}


# --------------------------------------------------------------------------

LEG_REF = re.compile(
    r"(lei(\s+complementar)?|decreto(-lei)?|medida provis[óo]ria|constitui[çc][ãa]o( federal)?|"
    r"c[óo]digo|art(igo)?s?\.?|inciso|al[íi]nea|par[áa]grafo|§|caput|n[ºo°]\.?|"
    r"\d[\d\.\-/º°]*|de \d+ de \w+ de \d+|janeiro|fevereiro|março|abril|maio|junho|julho|"
    r"agosto|setembro|outubro|novembro|dezembro)",
    re.IGNORECASE,
)
ABERTURA = re.compile(r"^\s*(altera|acrescenta|acresce|revoga|d[áa] nova reda[çc][ãa]o|"
                      r"inclui|modifica|insere|suprime)\b", re.IGNORECASE)
STOP = set("""a o e é de da do das dos em no na nos nas para por com sem que se ao aos à às
um uma uns umas os as sobre entre como ou seu sua seus suas outras outros outra outro
dá dar nova redação dispositivo dispositivos altera acrescenta revoga inclui modifica
insere suprime federal providências dispõe estabelece dá""".split())


def palavras_conteudo(ementa: str) -> int:
    t = LEG_REF.sub(" ", ementa.lower())
    t = re.sub(r"[^\wà-ú]+", " ", t)
    return sum(1 for w in t.split() if w not in STOP and len(w) > 2)


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower().strip().rstrip("."))


def md(df: pd.DataFrame, index=True) -> str:
    d = df.reset_index() if index else df
    head = "| " + " | ".join(map(str, d.columns)) + " |"
    sep = "| " + " | ".join("---" for _ in d.columns) + " |"
    rows = ["| " + " | ".join(str(v).replace("|", "/") for v in r) + " |" for r in d.values]
    return "\n".join([head, sep, *rows])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--temas", required=True, type=Path)
    ap.add_argument("--saida", default="data/processed/investigacoes", type=Path)
    ap.add_argument("--seed", default=42, type=int)
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    base = pd.read_parquet(a.base)
    temas = pd.read_parquet(a.temas)
    base["conj"] = base["temas_cod"].map(lambda x: frozenset(int(v) for v in x))
    base["ementa_norm"] = base["ementa"].fillna("").map(normalizar)
    nome_tema = temas.drop_duplicates("codTema").set_index("codTema")["tema"]
    out = ["# Investigações antes do portão G1\n"]

    # 1. Picos de volume -------------------------------------------------------
    out.append("## 1. Picos de volume mensal\n")
    por_mes = base.groupby("ano_mes").size()
    mediana = por_mes[por_mes > 50].median()
    picos = por_mes[por_mes > 1.8 * mediana].sort_values(ascending=False)
    out.append(f"Mediana mensal (meses com mais de 50): {mediana:.0f}. "
               f"Meses acima de 1,8 vezes a mediana: {', '.join(picos.index)}\n")
    for mes in picos.index:
        g = base[base["ano_mes"] == mes]
        aut = g["autor1_nome"].value_counts().head(5)
        dup = g["ementa_norm"].duplicated(keep=False).mean()
        tem = Counter(t for s in g["conj"] for t in s).most_common(5)
        out.append(f"### {mes} (n = {len(g)})\n")
        out.append(f"- Top 5 autores somam {aut.sum()} proposições ({aut.sum() / len(g):.1%}); "
                   f"ementas repetidas dentro do mês: {dup:.1%}")
        out.append("- Autores: " + "; ".join(f"{k} ({v})" for k, v in aut.items()))
        out.append("- Temas: " + "; ".join(f"{nome_tema.get(k, k)} ({v})" for k, v in tem))
        top = aut.index[0]
        ex = g.loc[g["autor1_nome"] == top, "ementa"].head(3).tolist()
        out.append(f"- Exemplos de {top}: " + " // ".join(e[:140] for e in ex) + "\n")

    # 2. Ementas idênticas ------------------------------------------------------
    out.append("## 2. Ementas idênticas\n")
    grupos = base[base["ementa_norm"].duplicated(keep=False)].groupby("ementa_norm")
    resumo = grupos.agg(n=("id", "size"),
                        autores=("autor1_nome", "nunique"),
                        conjuntos=("conj", lambda s: len(set(s))))
    out.append(f"- Grupos de ementas idênticas: {len(resumo)} (com {resumo['n'].sum()} proposições)")
    out.append(f"- Grupos com um único autor: {(resumo['autores'] == 1).mean():.1%}")
    out.append(f"- Grupos em que todas têm exatamente os mesmos temas oficiais: "
               f"{(resumo['conjuntos'] == 1).mean():.1%}")
    out.append(f"- Grupos com temas discordantes: {(resumo['conjuntos'] > 1).sum()} "
               "(lista em duplicatas_discordantes.csv). Isso é uma medida direta de "
               "inconsistência da indexação manual, útil para a Introdução e a Discussão.\n")
    disc = resumo[resumo["conjuntos"] > 1].index
    (base[base["ementa_norm"].isin(disc)]
        .assign(temas=lambda d: d["conj"].map(lambda s: "; ".join(str(nome_tema.get(t, t)) for t in sorted(s))))
        [["ementa_norm", "id", "siglaTipo", "dataApresentacao", "autor1_nome", "temas"]]
        .sort_values(["ementa_norm", "dataApresentacao"])
        .to_csv(a.saida / "duplicatas_discordantes.csv", index=False))
    out.append("Maiores grupos:\n")
    top_dup = resumo.sort_values("n", ascending=False).head(10).copy()
    top_dup.index = [i[:90] for i in top_dup.index]
    out.append(md(top_dup) + "\n")

    # 3. Partido da época e grafia das siglas ------------------------------------
    out.append("## 3. Partido do primeiro autor por ano\n")
    dep = base[base["autor1_eh_deputado"].fillna(False)].copy()
    dep["ano_ap"] = pd.to_datetime(dep["dataApresentacao"]).dt.year
    chave = ["PSL", "DEM", "UNIÃO", "PR", "PL", "PRB", "REPUBLIC", "PPS", "CIDADANIA",
             "PTB", "PATRIOTA", "PATRI", "PRD", "PROS", "SOLIDARI", "SOLIDARIED", "PSC", "PHS", "PODE"]
    ct = pd.crosstab(dep["autor1_partido"], dep["ano_ap"]).reindex([p for p in chave if p in set(dep["autor1_partido"])])
    out.append("Se as siglas extintas (PSL, DEM, PTB, PROS, PSC...) só aparecem até o ano da "
               "fusão e as sucessoras só depois, o arquivo traz o partido da época.\n")
    out.append(md(ct) + "\n")
    trocas = (dep.dropna(subset=["autor1_idDeputado"])
                 .groupby("autor1_idDeputado")["autor1_partido"].nunique())
    out.append(f"- Deputados com mais de uma sigla ao longo do período: {(trocas > 1).sum()} "
               f"de {len(trocas)}. Se fosse zero, o arquivo estaria trazendo o partido atual.\n")

    # 4. Formulaicas -------------------------------------------------------------
    out.append("## 4. Ementas formulaicas (critério preliminar)\n")
    base["abre_formula"] = base["ementa"].fillna("").str.match(ABERTURA)
    base["n_conteudo"] = base["ementa"].fillna("").map(palavras_conteudo)
    linhas = []
    for k in (1, 2, 3, 4):
        f = base["abre_formula"] & (base["n_conteudo"] <= k)
        linhas.append({"K": k, "n": int(f.sum()), "pct": f"{f.mean():.2%}"})
    out.append(f"- Começam com Altera/Acrescenta/Revoga/...: {base['abre_formula'].mean():.1%}")
    out.append(f"- Até 40 caracteres: {(base['len_ementa'] <= 40).sum()}")
    out.append("\nAbertura formulaica e no máximo K palavras de conteúdo:\n")
    out.append(md(pd.DataFrame(linhas), index=False) + "\n")
    # Amostra para anotação: estratificada, com sobre-representação das candidatas
    cand = base[base["abre_formula"] & (base["n_conteudo"] <= 4)]
    resto = base.drop(cand.index)
    amostra = pd.concat([
        cand.sample(min(150, len(cand)), random_state=a.seed),
        resto[resto["abre_formula"]].pipe(lambda d: d.sample(min(75, len(d)), random_state=a.seed)),
        resto[~resto["abre_formula"]].pipe(lambda d: d.sample(min(75, len(d)), random_state=a.seed)),
    ])
    amostra[["id", "siglaTipo", "ementa", "len_ementa", "abre_formula", "n_conteudo"]] \
        .assign(tema_inferivel="") \
        .sample(frac=1, random_state=a.seed) \
        .to_csv(a.saida / "amostra_formulaicas.csv", index=False)
    out.append("Amostra de 300 para anotar em amostra_formulaicas.csv "
               "(coluna tema_inferivel: s ou n).\n")

    # 5. Relevância dos temas ----------------------------------------------------
    out.append("## 5. Campo relevancia\n")
    if "relevancia" in temas.columns:
        vc = temas["relevancia"].value_counts(dropna=False).head(10).rename("n").to_frame()
        out.append("Se só existe um valor, não há tema principal no gabarito.\n")
        out.append(md(vc) + "\n")
    else:
        out.append("Coluna ausente.\n")

    # 6. Apensadas x principal ---------------------------------------------------
    out.append("## 6. Apensadas e proposição principal\n")
    if "idPropPrincipal" in base.columns:
        conj_por_id = base.set_index("id")["conj"]
        ap_ = base[base["idPropPrincipal"].notna() & base["idPropPrincipal"].isin(conj_por_id.index)]
        comp = [len(s & conj_por_id[p]) > 0 for s, p in zip(ap_["conj"], ap_["idPropPrincipal"])]
        out.append(f"- Apensadas cuja principal também está no recorte: {len(ap_)}")
        out.append(f"- Dessas, compartilham ao menos um tema com a principal: {np.mean(comp):.1%}")
        out.append("- Esses pares viram uma checagem extra na Fase 4: quantos caem no mesmo cluster.\n")

    # 7. BCubed: referências antes de qualquer modelo ----------------------------
    out.append("## 7. BCubed estendido: referências para calibrar a Fase 4\n")
    out.append("Com 2,1 temas por proposição e um tema presente em quase 30% do corpus, "
               "até agrupamentos sem sentido pontuam alto em precisão, e o recall tem teto "
               "abaixo de 1 porque cada proposição fica em um único cluster.\n")
    rot = list(base["conj"])
    freq = Counter(t for s in rot for t in s)
    mais_freq = np.array([max(s, key=lambda t: freq[t]) if s else -1 for s in rot])
    menos_freq = np.array([min(s, key=lambda t: freq[t]) if s else -1 for s in rot])
    exato = pd.factorize(pd.Series([tuple(sorted(s)) for s in rot]))[0]
    refs = {
        "Um cluster só": np.zeros(len(rot), dtype=int),
        "Cada proposição sozinha": np.arange(len(rot)),
        "Aleatório, 32 clusters (média de 5 seeds)": None,
        "Gabarito: tema mais frequente da proposição": mais_freq,
        "Gabarito: tema menos frequente da proposição": menos_freq,
        "Gabarito: conjunto exato de temas": exato,
    }
    linhas = []
    for nome, cl in refs.items():
        if cl is None:
            rs = [bcubed_estendido(rng.permutation(mais_freq), rot) for _ in range(5)]
            r = {k: np.mean([x[k] for x in rs]) for k in ("P", "R", "F")}
        else:
            r = bcubed_estendido(cl, rot)
        linhas.append({"referência": nome, "P": f"{r['P']:.3f}", "R": f"{r['R']:.3f}", "F": f"{r['F']:.3f}"})
    out.append(md(pd.DataFrame(linhas), index=False) + "\n")
    out.append("O modelo precisa ficar claramente acima da linha aleatória. As linhas de "
               "gabarito mostram quanto um agrupamento rígido consegue chegar quando sabe "
               "a resposta, e servem de referência superior na discussão.\n")

    (a.saida / "investigacoes_g1.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Relatório em {a.saida / 'investigacoes_g1.md'}")


if __name__ == "__main__":
    main()