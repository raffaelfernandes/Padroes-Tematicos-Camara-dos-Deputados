"""
fase2_criterio_formulaicas.py

Critério para identificar ementas formulaicas: ementas que só fazem referência
a dispositivos legais e não permitem inferir o tema da proposição.

Uma ementa é formulaica quando as três condições valem:
  1. começa com um verbo de alteração (Altera, Acrescenta, Revoga, Dá nova
     redação, Inclui, Modifica, Insere, Suprime), ignorando aspas iniciais;
  2. não cita a lei pelo nome (Código Penal, Estatuto do Idoso, Lei das
     Eleições, CLT, Marco Civil...) nem descreve o objeto da lei
     ("que dispõe sobre...", "que institui...");
  3. depois de remover referências legais (números, artigos, parágrafos,
     incisos, datas), vocabulário estrutural (redação, caput, capítulo,
     texto, dispositivo...) e stopwords, sobram no máximo K palavras de
     conteúdo. K = 1 por padrão.

Uso como módulo:
    from fase2_criterio_formulaicas import eh_formulaica
    eh_formulaica("Altera o Decreto-Lei nº 2.848, de 1940.")   # True

Uso para validar contra uma amostra anotada (coluna tema_inferivel = s/n):
    uv run python src/fase2_criterio_formulaicas.py avaliar amostra_anotada.csv
"""

from __future__ import annotations

import argparse
import re

ABERTURA = re.compile(
    r"^[\s\"'“”«»]*(altera(-se)?|acrescenta(-se)?|acresce|revoga|d[áa] nova reda[çc][ãa]o|"
    r"inclui|modifica|insere|suprime)\b",
    re.IGNORECASE,
)

REF_LEGAL = re.compile(
    r"(lei(\s+complementar)?|decreto(-?\s?lei)?|medida provis[óo]ria|constitui[çc][ãa]o( federal)?|"
    r"c[óo]digo|art(igo)?s?\.?|inciso|al[íi]nea|par[áa]grafo|§|caput|n[ºo°]\.?|"
    r"\d[\d\.\-/º°]*|de \d+ de \w+ de \d+|janeiro|fevereiro|março|abril|maio|junho|julho|"
    r"agosto|setembro|outubro|novembro|dezembro)",
    re.IGNORECASE,
)

NOME_LEI = re.compile(
    r"(?i:c[óo]digo\s+(de\s+|do\s+|da\s+)?\w{3,}|estatuto|consolida[çc][ãa]o das leis|marco (civil|legal))|"
    r"\b(?i:leis?)\s+(de|do|da|das|dos)\s+[A-ZÁÉÍÓÚÂÊÔ]|"
    r"\b(?i:leis?)\s+(?!Complementar|Federal|Ordin|Org[âa]nica|Delegada|Estadual|Municipal|Constitucional)"
    r"[A-ZÁÉÍÓÚ][a-zá-ú]+|"
    r"\b(?i:que)\s+[\"'“”]?(?i:disp[õo]e|institui|estabelece|cria|regula|regulamenta)\b",
)

ROMANO = re.compile(r"\b[ivxlc]+\b")

STOP = set("""a o e é de da do das dos em no na nos nas para por com sem que se ao aos à às
um uma uns umas os as sobre entre como ou seu sua seus suas outras outros outra outro
dá dar nova novo novos novas redação dispositivo dispositivos altera acrescenta revoga inclui
modifica insere suprime federal providências providencias dispõe estabelece
capítulo capitulo seção secao título titulo texto seguinte seguintes redacao caput alínea alinea
alíneas alineas incluir acrescentar acrescentando inserir alterar modificar revogar suprimir
referida referido termos especifica parte item itens anexo letra lei leis complementar
complementares nºs mesma mesmo ambos ambas""".split())


def palavras_conteudo(ementa: str) -> int:
    t = REF_LEGAL.sub(" ", ementa.lower())
    t = re.sub(r"[^\wà-ú]+", " ", t)
    t = ROMANO.sub(" ", t)
    return sum(1 for w in t.split() if w not in STOP and len(w) > 2)


def cita_nome_lei(ementa: str) -> bool:
    return bool(NOME_LEI.search(ementa))


def eh_formulaica(ementa: str | None, K: int = 1) -> bool:
    if not ementa or not ementa.strip():
        return True
    return bool(ABERTURA.match(ementa)) and not cita_nome_lei(ementa) and palavras_conteudo(ementa) <= K


# --------------------------------------------------------------------------

def avaliar(caminho: str, corpus: int, frac_abertura: float, candidatas: int) -> None:
    import numpy as np
    import pandas as pd

    d = pd.read_csv(caminho)
    y = d["tema_inferivel"].astype(str).str.strip().str.lower().eq("n")
    # Pesos para estimar no corpus: a amostra sobre-representa as candidatas.
    estrato = np.where(d["abre_formula"] & (d["n_conteudo"] <= 4), "cand",
                       np.where(d["abre_formula"], "abre_resto", "sem_abre"))
    n_abre = round(frac_abertura * corpus)
    pop = {"cand": candidatas, "abre_resto": n_abre - candidatas, "sem_abre": corpus - n_abre}
    tam = pd.Series(estrato).value_counts()
    w = pd.Series([pop[e] / tam[e] for e in estrato])

    linhas = []
    for K in range(0, 5):
        pred = d["ementa"].map(lambda e: eh_formulaica(e, K))
        for nome, ww in (("amostra", pd.Series(1.0, index=d.index)), ("corpus", w)):
            tp, pp, pn = (ww * (pred & y)).sum(), (ww * pred).sum(), (ww * y).sum()
            P, R = (tp / pp if pp else float("nan")), tp / pn
            linhas.append({"K": K, "escala": nome, "previstas": int(pred.sum()),
                           "P": round(P, 3), "R": round(R, 3),
                           "F1": round(2 * P * R / (P + R), 3) if P + R else 0,
                           "formulaicas_estimadas": int(round(pp)) if nome == "corpus" else ""})
    print(pd.DataFrame(linhas).to_string(index=False))
    for K in (1,):
        pred = d["ementa"].map(lambda e: eh_formulaica(e, K))
        fp, fn = d[pred & ~y], d[~pred & y]
        print(f"\nK={K}: {len(fp)} falsos positivos, {len(fn)} falsos negativos")
        for titulo, df in (("Falsos positivos (regra diz formulaica, anotação s)", fp),
                           ("Falsos negativos (anotação n, regra não pega)", fn)):
            if len(df):
                print(f"\n{titulo}:")
                for _, r in df.iterrows():
                    print(f"  [{r['id']}] {r['ementa'][:160]}")


def amostrar(base: str, excluir: list[str], n: int, K: int, saida: str, seed: int) -> None:
    """Amostra de validação: metade marcada como formulaica pela regra (mede a
    precisão) e metade com abertura formulaica que a regra NÃO marcou (onde
    ficam os erros de recall). Sai sem nenhuma coluna da regra, para não
    influenciar a anotação; o gabarito da regra fica num arquivo separado."""
    import pandas as pd

    b = pd.read_parquet(base)[["id", "siglaTipo", "ementa"]]
    vistos: set = set()
    for c in excluir:
        vistos |= set(pd.read_csv(c)["id"])
    b = b[~b["id"].isin(vistos)].copy()
    b["regra"] = b["ementa"].map(lambda e: eh_formulaica(e, K))
    b["abre"] = b["ementa"].fillna("").str.match(ABERTURA)
    metade = n // 2
    a1 = b[b["regra"]].sample(min(metade, int(b["regra"].sum())), random_state=seed)
    pool = b[b["abre"] & ~b["regra"]]
    a2 = pool.sample(min(n - len(a1), len(pool)), random_state=seed)
    am = pd.concat([a1.assign(estrato="regra_sim"), a2.assign(estrato="regra_nao_abre")])
    am = am.sample(frac=1, random_state=seed)
    am[["id", "siglaTipo", "ementa"]].assign(tema_inferivel="", obs="").to_csv(saida, index=False)
    oculto = saida.replace(".csv", "_gabarito_regra.csv")
    am[["id", "estrato", "regra"]].to_csv(oculto, index=False)
    print(f"{len(am)} ementas em {saida}. Não abra {oculto} antes de terminar a anotação.")
    print(f"No corpus: {int(b['regra'].sum())} marcadas pela regra; "
          f"{len(pool)} com abertura formulaica não marcadas.")


def validar(anotada: str, gabarito: str, base: str) -> None:
    """Precisão e recall na amostra nova, com pesos para estimar no corpus."""
    import pandas as pd

    d = pd.read_csv(anotada).merge(pd.read_csv(gabarito), on="id")
    d = d[d["tema_inferivel"].astype(str).str.strip().str.lower().isin(["s", "n"])]
    y = d["tema_inferivel"].str.strip().str.lower().eq("n")
    b = pd.read_parquet(base)[["ementa"]]
    regra = b["ementa"].map(eh_formulaica)
    pop = {"regra_sim": int(regra.sum()),
           "regra_nao_abre": int((b["ementa"].fillna("").str.match(ABERTURA) & ~regra).sum())}
    tam = d["estrato"].value_counts()
    w = d["estrato"].map(lambda e: pop[e] / tam[e])
    pred = d["regra"].astype(bool)
    P = (w * (pred & y)).sum() / (w * pred).sum()
    R = (w * (pred & y)).sum() / (w * y).sum()
    print(f"Amostra de validação: {len(d)} ementas anotadas")
    print(f"Precisão: {P:.3f}   Recall (dentro das ementas com abertura formulaica): {R:.3f}")
    print(f"Formulaicas estimadas no corpus: {(w * y).sum():.0f}")
    for titulo, m in (("Falsos positivos", pred & ~y), ("Falsos negativos", ~pred & y)):
        if m.any():
            print(f"\n{titulo}:")
            for _, r in d[m].iterrows():
                print(f"  [{r['id']}] {r['ementa'][:160]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("avaliar", help="métricas por K na amostra de desenvolvimento")
    a.add_argument("csv")
    a.add_argument("--corpus", type=int, default=40006)
    a.add_argument("--frac-abertura", type=float, default=0.486)
    a.add_argument("--candidatas", type=int, default=1462,
                   help="candidatas da regra antiga (abertura e até 4 palavras) no corpus")
    s = sub.add_parser("amostrar", help="gera amostra nova para validação")
    s.add_argument("--base", required=True)
    s.add_argument("--excluir", nargs="*", default=[])
    s.add_argument("--n", type=int, default=100)
    s.add_argument("--K", type=int, default=1)
    s.add_argument("--saida", default="amostra_validacao.csv")
    s.add_argument("--seed", type=int, default=7)
    v = sub.add_parser("validar", help="métricas na amostra de validação anotada")
    v.add_argument("csv")
    v.add_argument("--gabarito", required=True)
    v.add_argument("--base", required=True)
    args = ap.parse_args()
    if args.cmd == "avaliar":
        avaliar(args.csv, args.corpus, args.frac_abertura, args.candidatas)
    elif args.cmd == "amostrar":
        amostrar(args.base, args.excluir, args.n, args.K, args.saida, args.seed)
    else:
        validar(args.csv, args.gabarito, args.base)