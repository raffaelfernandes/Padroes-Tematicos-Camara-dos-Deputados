"""
sensibilidade_rq2.py

Extra da revisão final do TCC (14/11/2026). Mede quanto as assinaturas partidárias da RQ2 dependem
das duas escolhas livres do método: a força do prior de Dirichlet (a0) e o percentil da produção por
deputado usado como limite do peso (C). Refaz a RQ2 (versão com todas as proposições, modelo principal)
numa grade de valores e compara cada conjunto de assinaturas partidárias com o do texto (a0 = 500,
percentil 90).

Uso (a partir de code/):
    uv run python src/extras/sensibilidade_rq2.py
Saídas em data/processed/fase5/sensibilidade_rq2.csv e sensibilidade_rq2.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
import fase5_rqs as f5  # noqa: E402

P = Path("data/processed")
TOPICOS = P / "fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet"
A0S = [100, 250, 500, 1000, 2000]
PCTS = [75, 90, 95, 100]   # 100 = sem limite efetivo (peso 1 para todos)


def main() -> None:
    base = sorted(P.glob("base_fase2_*.parquet"))[-1]
    d, nomes = f5.carregar(base, TOPICOS)
    ref = {}
    linhas = []
    for leg in (56, 57):
        r, _ = f5.rq2(d, nomes, leg)
        ref[leg] = set(zip(r.loc[r["assinatura"] == "partidária", "partido"], r.loc[r["assinatura"] == "partidária", "topico"]))
    for leg in (56, 57):
        for a0 in A0S:
            for pct in PCTS:
                r, C = f5.rq2(d, nomes, leg, a0=a0, pct=pct)
                s = set(zip(r.loc[r["assinatura"] == "partidária", "partido"], r.loc[r["assinatura"] == "partidária", "topico"]))
                inter = len(s & ref[leg])
                linhas.append({"legislatura": leg, "a0": a0, "percentil": pct, "C": round(C, 1),
                               "assinaturas": len(s), "partidos_com_assinatura": len({p for p, _ in s}),
                               "mantidas_do_texto": inter, "pct_mantidas_do_texto": round(inter / len(ref[leg]), 3) if ref[leg] else None,
                               "novas": len(s - ref[leg]),
                               "jaccard_com_texto": round(inter / len(s | ref[leg]), 3) if (s | ref[leg]) else None})
    t = pd.DataFrame(linhas)
    (P / "fase5").mkdir(parents=True, exist_ok=True)
    t.to_csv(P / "fase5/sensibilidade_rq2.csv", index=False)
    resumo = t.groupby("legislatura").agg(min_mantidas=("pct_mantidas_do_texto", "min"),
                                          med_mantidas=("pct_mantidas_do_texto", "median"),
                                          min_jaccard=("jaccard_com_texto", "min"),
                                          med_jaccard=("jaccard_com_texto", "median")).reset_index()
    rel = ["# Sensibilidade das assinaturas partidárias a a0 e ao percentil do limite\n",
           f"Referência (texto): a0 = 500 e percentil 90. Assinaturas partidárias de referência: "
           f"{len(ref[56])} na 56ª e {len(ref[57])} na 57ª.\n", t.to_markdown(index=False), "", resumo.to_markdown(index=False)]
    (P / "fase5/sensibilidade_rq2.md").write_text("\n".join(rel), encoding="utf-8")
    print("\n".join(rel))


if __name__ == "__main__":
    main()
