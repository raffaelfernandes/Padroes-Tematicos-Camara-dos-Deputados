"""
leis_citadas.py

Extra da revisão final do TCC (14/11/2026). Mede quanto os tópicos se organizam pela lei que a
ementa altera, e quanto a própria lei citada já antecipa o tema oficial.

1. Extrai da ementa original a primeira lei citada: pelo número (Lei, Lei Complementar, Decreto-Lei,
   Medida Provisória) ou pelo nome dos códigos e estatutos mais comuns, que são unificados com o número
   correspondente (por exemplo, "Código Penal" e "Decreto-Lei nº 2.848" viram a mesma lei).
2. Pureza de lei por tópico: entre as proposições que citam alguma lei, a fração que cita a lei mais
   comum do seu tópico (média ponderada pelos tópicos). Comparada com grupos sorteados com os mesmos
   tamanhos e entre os três modelos.
3. Quanto a lei antecipa o tema: fração dos pares de proposições que citam a mesma lei e dividem algum
   tema oficial, contra a mesma fração em pares quaisquer.

Lembrete: o texto enviado aos modelos não tem números nem datas de leis, mas mantém os nomes de leis e
códigos.

Uso (a partir de code/):
    uv run python src/extras/leis_citadas.py
Saídas em data/processed/fase4/leis_citadas.md e leis_citadas.csv.
"""
from __future__ import annotations

import re
from pathlib import Path

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from fase4_avaliacao import Gabarito  # noqa: E402

P = Path("data/processed")
MODELOS = {
    "BERTimbau": "bertimbau_nn30_mcs100_eom_ms10_rk",
    "Serafim": "serafim_nn30_mcs100_eom_ms5_rk",
    "e5": "e5_nn30_mcs100_eom_ms10_rk",
}
NOMES = [  # (padrão no texto, chave da lei)
    (r"c[óo]digo de processo penal", "DL 3689"),
    (r"c[óo]digo penal militar", "DL 1001"),
    (r"c[óo]digo penal", "DL 2848"),
    (r"c[óo]digo de processo civil", "L 13105"),
    (r"c[óo]digo civil", "L 10406"),
    (r"c[óo]digo de tr[âa]nsito", "L 9503"),
    (r"c[óo]digo de defesa do consumidor", "L 8078"),
    (r"c[óo]digo eleitoral", "L 4737"),
    (r"c[óo]digo tribut[áa]rio nacional", "L 5172"),
    (r"c[óo]digo florestal", "L 12651"),
    (r"consolida[çc][ãa]o das leis do trabalho", "DL 5452"),
    (r"estatuto da crian[çc]a e do adolescente", "L 8069"),
    (r"estatuto d[ao] (?:pessoa )?idos[ao]", "L 10741"),
    (r"estatuto da pessoa com defici[êe]ncia", "L 13146"),
    (r"estatuto do desarmamento", "L 10826"),
    (r"lei maria da penha", "L 11340"),
    (r"lei de diretrizes e bases", "L 9394"),
    (r"lei de execu[çc][ãa]o penal", "L 7210"),
    (r"lei de licita[çc][õo]es", "L 14133"),
    (r"lei org[âa]nica da sa[úu]de", "L 8080"),
]
NUM = re.compile(r"\b(lei complementar|lei|decreto-lei|medida provis[óo]ria)\s+n?[º°o\.]*\s*([\d\.]+)", re.I)
TIPO = {"lei complementar": "LC", "lei": "L", "decreto-lei": "DL"}


def primeira_lei(ementa: str) -> str | None:
    e = (ementa or "").lower()
    achados = []
    for pad, chave in NOMES:
        m = re.search(pad, e)
        if m:
            achados.append((m.start(), chave))
    for m in NUM.finditer(e):
        tipo = TIPO.get(m.group(1).lower(), "MP")
        num = m.group(2).replace(".", "").strip()
        if num:
            achados.append((m.start(), f"{tipo} {int(num)}"))
    return min(achados)[1] if achados else None


def pureza_lei(lab: np.ndarray, lei: np.ndarray) -> float:
    d = pd.DataFrame({"t": lab, "l": lei}).dropna()
    g = d.groupby("t")["l"]
    return float((g.agg(lambda s: s.value_counts().iloc[0]).sum()) / len(d))


def main() -> None:
    base = pd.read_parquet(sorted(P.glob("base_fase2_*.parquet"))[-1], columns=["id", "ementa", "eh_formulaica"])
    base["lei"] = base["ementa"].map(primeira_lei)
    temas = pd.read_parquet(P / "temas_long_20261027.parquet")
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    base["temas"] = base["id"].map(conj)
    cita = base["lei"].notna()
    rel = ["# Os tópicos se organizam pela lei citada?\n",
           f"Proposições que citam alguma lei identificável na ementa: {cita.sum()} ({cita.mean():.1%}). "
           f"Leis distintas: {base['lei'].nunique()}. Mais citadas: "
           + "; ".join(f"{k} ({v})" for k, v in base["lei"].value_counts().head(8).items()) + ".\n"]

    linhas = []
    rng = np.random.default_rng(130)
    for m, tag in MODELOS.items():
        t = pd.read_parquet(P / f"fase3/topicos_{tag}.parquet")[["id", "topico_alt_ctfidf"]]
        d = base.merge(t, on="id")
        lab, lei = d["topico_alt_ctfidf"].to_numpy(), d["lei"].to_numpy(dtype=object)
        lei = np.where(pd.isna(lei), None, lei)
        pz = pureza_lei(lab, lei)
        ale = np.mean([pureza_lei(rng.permutation(lab), lei) for _ in range(5)])
        # tópicos em que uma única lei responde por mais da metade das proposições que citam lei
        dd = pd.DataFrame({"t": lab, "l": lei}).dropna()
        dom = dd.groupby("t")["l"].agg(lambda s: s.value_counts(normalize=True).iloc[0])
        n_cit = dd.groupby("t").size()
        frac_cita = pd.Series(lei).notna().groupby(lab).mean()
        lei_dom = (dom > 0.5) & (n_cit >= 30)
        linhas.append({"modelo": m, "pureza_lei": round(pz, 3), "pureza_lei_acaso": round(float(ale), 3),
                       "topicos": int(len(dom)), "topicos_com_lei_dominante": int(lei_dom.sum()),
                       "fracao_proposicoes_nesses_topicos": round(float(pd.Series(lab).isin(dom[lei_dom].index).mean()), 3)})
    res = pd.DataFrame(linhas)
    res.to_csv(P / "fase4/leis_citadas.csv", index=False)
    rel += ["## Pureza de lei citada por tópico\n",
            "Fração das proposições (entre as que citam lei) que citam a lei mais comum do seu tópico. "
            "`topicos_com_lei_dominante`: tópicos com pelo menos 30 proposições que citam lei e em que uma lei "
            "responde por mais da metade delas.\n", res.to_markdown(index=False), ""]

    # quanto a lei antecipa o tema oficial
    x = base[cita & base["temas"].notna()]
    grupos = x.groupby("lei")["temas"].apply(list)
    comp, tot = 0, 0
    for ts in grupos:
        n = len(ts)
        if n < 2:
            continue
        if n > 400:   # amostra de pares nas leis muito citadas
            idx = rng.choice(n, size=(20000, 2))
            idx = idx[idx[:, 0] != idx[:, 1]]
            comp += sum(len(ts[i] & ts[j]) > 0 for i, j in idx) * (n * (n - 1) / 2) / len(idx)
            tot += n * (n - 1) / 2
        else:
            for i in range(n):
                for j in range(i + 1, n):
                    comp += len(ts[i] & ts[j]) > 0
            tot += n * (n - 1) / 2
    todos = base["temas"].dropna().tolist()
    idx = rng.choice(len(todos), size=(50000, 2))
    base_rate = np.mean([len(todos[i] & todos[j]) > 0 for i, j in idx if i != j])
    rel += ["## A lei citada antecipa o tema oficial?\n",
            f"Pares de proposições que citam a mesma lei e dividem algum tema oficial: {comp / tot:.1%}. "
            f"Pares quaisquer: {base_rate:.1%}.\n"]
    # BCubed separado nas ementas com e sem lei citada: a vantagem de um modelo some sem a pista da lei?
    linhas_b = []
    bt = base.dropna(subset=["temas"])
    for nome, mask in (("sem lei citada", bt["lei"].isna()), ("com lei citada", bt["lei"].notna())):
        b = bt[mask]
        g = Gabarito(list(b["temas"]))
        for m, tag in MODELOS.items():
            lab = pd.read_parquet(P / f"fase3/topicos_{tag}.parquet").set_index("id")["topico_alt_ctfidf"].reindex(b["id"]).to_numpy()
            r = g.bcubed(lab)
            p_ale = np.mean([g.bcubed(rng.permutation(lab))["P"] for _ in range(3)])
            linhas_b.append({"subconjunto": nome, "proposicoes": len(b), "modelo": m,
                             "P": round(r["P"], 3), "R": round(r["R"], 3), "P_acaso": round(float(p_ale), 3)})
    rel += ["## BCubed nas ementas com e sem lei citada\n", pd.DataFrame(linhas_b).to_markdown(index=False), ""]
    # tópicos do BERTimbau com lei dominante
    t = pd.read_parquet(P / f"fase3/topicos_{MODELOS['BERTimbau']}.parquet")[["id", "topico_alt_ctfidf"]]
    d = base.merge(t, on="id").dropna(subset=["lei"])
    tab = (d.groupby("topico_alt_ctfidf")["lei"].agg(lambda s: (s.value_counts().index[0], round(s.value_counts(normalize=True).iloc[0], 2), len(s)))
             .apply(pd.Series).rename(columns={0: "lei_mais_comum", 1: "fracao", 2: "citam_lei"}))
    tab = tab[(tab["fracao"] > 0.5) & (tab["citam_lei"] >= 30)].sort_values("fracao", ascending=False).reset_index()
    rel += ["## BERTimbau: tópicos em que uma lei responde por mais da metade das citações\n", tab.to_markdown(index=False)]
    (P / "fase4/leis_citadas.md").write_text("\n".join(rel), encoding="utf-8")
    print("\n".join(rel))


if __name__ == "__main__":
    main()
