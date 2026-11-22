"""
inconsistencias_cedi.py

Extra da revisão final do TCC (14/11/2026). Testa se a vizinhança semântica dos embeddings ajuda a
achar possíveis inconsistências na classificação temática do CEDI.

Ideia: para cada proposição substantiva, olha as 15 proposições mais parecidas (cosseno no espaço
original do BERTimbau, sem contar textos idênticos). Um par (proposição, tema oficial) é "isolado"
quando nenhuma das 15 vizinhas tem aquele tema. A pergunta é se os pares isolados concentram mais
temas inadequados do que pares comuns.

Desenho da anotação (cego): 40 pares isolados e 20 pares de controle (o tema aparece em pelo menos
uma vizinha) são sorteados e embaralhados. O anotador vê a ementa, o tema avaliado, os outros temas
oficiais e o tema mais comum entre as vizinhas que a proposição não tem ("tema sugerido"), sem saber
de que grupo veio cada item. As regras estão em anotacoes/cedi_inconsistencias_INSTRUCOES.md.

Subcomandos (a partir de code/):
    uv run python src/extras/inconsistencias_cedi.py amostrar
    uv run python src/extras/inconsistencias_cedi.py resumir

Arquivos:
    anotacoes/cedi_inconsistencias.csv          planilha para anotar (colunas tema_adequado e sugerido_se_aplica)
    anotacoes/cedi_inconsistencias_OCULTO.csv   grupo de cada item (não abrir antes de terminar)
    data/processed/fase4/inconsistencias_cedi.md  resumo depois da anotação
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

P = Path("data/processed")
ANOT = Path("anotacoes")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seed import SEED  # noqa: E402  (130; ver src/seed.py)
K = 15
N_ISOLADOS, N_CONTROLE = 40, 20
PLANILHA = ANOT / "cedi_inconsistencias.csv"
OCULTO = ANOT / "cedi_inconsistencias_OCULTO.csv"

INSTRUCOES = """# Anotação: possíveis inconsistências na classificação do CEDI

Cada linha traz uma proposição, um **tema avaliado** (um dos temas oficiais dela), os outros temas
oficiais e um **tema sugerido**. Leia só a ementa (pode abrir a ementa detalhada no site da Câmara se
a ementa for curta demais) e preencha duas colunas.

## tema_adequado
O tema avaliado descreve o assunto da proposição?
- **A** (adequado): o tema descreve a finalidade ou o objeto principal da proposição.
- **P** (parcial): o tema tem relação, mas é secundário ou indireto (por exemplo, só porque a lei
  alterada é daquela área, sem a proposição tratar do assunto).
- **I** (inadequado): o tema não tem relação reconhecível com a ementa.

## sugerido_se_aplica
O tema sugerido também descreveria a proposição?
- **S** (sim), **N** (não). Deixe em branco se não houver tema sugerido.

## Regras fixadas antes da anotação
1. Julgar pela finalidade da proposição, e não pelas leis que ela altera (a mesma regra da anotação dos outliers).
2. Não consultar o resultado do modelo nem o arquivo OCULTO antes de terminar.
3. Na dúvida entre A e P, marcar P; na dúvida entre P e I, marcar P.
4. A coluna `obs` é livre, para casos que mereçam comentário.
"""


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def vizinhos(emb: np.ndarray, k: int, lote: int = 2000) -> np.ndarray:
    """k vizinhos por cosseno (vetores já normalizados), excluindo o próprio texto."""
    out = np.empty((len(emb), k), dtype=np.int64)
    for i in range(0, len(emb), lote):
        s = emb[i:i + lote] @ emb.T
        s[np.arange(len(s)), np.arange(i, i + len(s))] = -np.inf
        idx = np.argpartition(-s, k, axis=1)[:, :k]
        ordem = np.argsort(-np.take_along_axis(s, idx, 1), axis=1)
        out[i:i + lote] = np.take_along_axis(idx, ordem, 1)
    return out


def amostrar(a) -> None:
    ANOT.mkdir(exist_ok=True)
    if PLANILHA.exists() and not a.refazer:
        raise SystemExit(f"{PLANILHA} já existe. Use --refazer para sortear de novo (perde a anotação).")
    u = pd.read_parquet(P / "embeddings" / "textos_unicos.parquet")
    emb = np.load(P / "embeddings" / "emb_bertimbau.npy").astype(np.float32)
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    base = pd.read_parquet(a.base, columns=["id", "id_texto_unico", "ementa", "eh_formulaica", "siglaTipo", "numero", "ano"])
    temas = pd.read_parquet(a.temas)
    nome = temas.drop_duplicates("codTema").set_index("codTema")["tema"].to_dict()
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    base["temas"] = base["id"].map(conj)
    # um texto único pode ter várias proposições; usa-se a primeira de cada texto, com tema
    sub = base[~base["eh_formulaica"] & base["temas"].notna()].drop_duplicates("id_texto_unico").copy()
    pos_u = pd.Series(np.arange(len(u)), index=u["id_texto_unico"])
    sub["pos"] = pos_u.loc[sub["id_texto_unico"]].to_numpy()
    E = emb[sub["pos"].to_numpy()]
    print(f"Calculando {K} vizinhos para {len(sub)} proposições...")
    viz = vizinhos(E, K)
    temas_arr = sub["temas"].to_numpy()
    linhas = []
    for i, (pid, ts) in enumerate(zip(sub["id"], temas_arr)):
        cont = pd.Series([t for j in viz[i] for t in temas_arr[j]]).value_counts()
        sugest = [t for t in cont.index if t not in ts]
        for t in ts:
            linhas.append({"id": pid, "tema": t, "vizinhas_com_tema": int(cont.get(t, 0)),
                           "tema_sugerido": sugest[0] if sugest else None,
                           "vizinhas_com_sugerido": int(cont[sugest[0]]) if sugest else 0})
    pares = pd.DataFrame(linhas)
    pares["isolado"] = pares["vizinhas_com_tema"] == 0
    pares.to_parquet(P / "fase4" / "inconsistencias_pares.parquet", index=False)
    print(f"{len(pares)} pares (proposição, tema); isolados: {pares['isolado'].sum()} "
          f"({pares['isolado'].mean():.1%}); proposições com algum tema isolado: "
          f"{pares.groupby('id')['isolado'].any().mean():.1%}")

    rng = np.random.default_rng(SEED)
    iso = pares[pares["isolado"]].sample(N_ISOLADOS, random_state=SEED).assign(grupo="isolado")
    ctl = pares[~pares["isolado"] & ~pares["id"].isin(iso["id"])].sample(N_CONTROLE, random_state=SEED).assign(grupo="controle")
    amostra = pd.concat([iso, ctl]).sample(frac=1, random_state=SEED).reset_index(drop=True)
    amostra["item"] = np.arange(1, len(amostra) + 1)
    info = base.set_index("id")
    amostra["proposicao"] = [f"{info.at[i, 'siglaTipo']} {info.at[i, 'numero']}/{info.at[i, 'ano']}" for i in amostra["id"]]
    amostra["ementa"] = [info.at[i, "ementa"] for i in amostra["id"]]
    amostra["tema_avaliado"] = amostra["tema"].map(nome)
    amostra["outros_temas_oficiais"] = [
        "; ".join(sorted(nome[t] for t in info.at[i, "temas"] if t != tt)) for i, tt in zip(amostra["id"], amostra["tema"])]
    amostra["tema_sugerido_nome"] = amostra["tema_sugerido"].map(lambda t: nome.get(t, "") if pd.notna(t) else "")
    vis = amostra[["item", "proposicao", "ementa", "tema_avaliado", "outros_temas_oficiais", "tema_sugerido_nome"]].rename(
        columns={"tema_sugerido_nome": "tema_sugerido"})
    vis["tema_adequado"] = ""
    vis["sugerido_se_aplica"] = ""
    vis["obs"] = ""
    vis.to_csv(PLANILHA, index=False, encoding="utf-8-sig")
    amostra[["item", "id", "grupo", "tema", "vizinhas_com_tema", "tema_sugerido", "vizinhas_com_sugerido"]].to_csv(
        OCULTO, index=False, encoding="utf-8-sig")
    (ANOT / "cedi_inconsistencias_INSTRUCOES.md").write_text(INSTRUCOES, encoding="utf-8")
    print(f"Planilha: {PLANILHA} ({len(vis)} itens). Instruções: {ANOT / 'cedi_inconsistencias_INSTRUCOES.md'}")


def resumir(a) -> None:
    v = pd.read_csv(PLANILHA, encoding="utf-8-sig", dtype=str).fillna("")
    o = pd.read_csv(OCULTO, encoding="utf-8-sig")
    
    # Normaliza a chave usada no relacionamento
    v["item"] = v["item"].astype("string").str.strip()
    o["item"] = o["item"].astype("string").str.strip()

    d = v.merge(o, on="item")
    
    d = v.merge(o, on="item")
    d["tema_adequado"] = d["tema_adequado"].str.strip().str.upper()
    d["sugerido_se_aplica"] = d["sugerido_se_aplica"].str.strip().str.upper()
    falta = d["tema_adequado"].eq("").sum()
    if falta:
        print(f"Atenção: {falta} itens sem tema_adequado; ficam de fora do resumo.")
    d = d[d["tema_adequado"].isin(["A", "P", "I"])]
    pares = pd.read_parquet(P / "fase4" / "inconsistencias_pares.parquet")
    rel = ["# Possíveis inconsistências na classificação do CEDI\n",
           f"Pares (proposição, tema oficial) nas ementas substantivas: {len(pares)}; isolados (nenhuma das {K} "
           f"vizinhas tem o tema): {pares['isolado'].sum()} ({pares['isolado'].mean():.1%}). Proposições com algum "
           f"tema isolado: {pares.groupby('id')['isolado'].any().mean():.1%}.\n",
           "## Adequação do tema avaliado (IC de Wilson de 95%)\n",
           "| Grupo | n | Adequado | Parcial | Inadequado | Parcial ou inadequado |", "|---|---|---|---|---|---|"]
    for g in ("isolado", "controle"):
        x = d[d["grupo"] == g]
        n = len(x)
        cel = []
        for cat in (["A"], ["P"], ["I"], ["P", "I"]):
            k = int(x["tema_adequado"].isin(cat).sum())
            lo, hi = wilson(k, n)
            cel.append(f"{k} ({k / n:.0%}; {lo:.0%} a {hi:.0%})" if n else "-")
        rel.append(f"| {g} | {n} | " + " | ".join(cel) + " |")
    s = d[d["sugerido_se_aplica"].isin(["S", "N"])]
    rel += ["", "## O tema sugerido pelas vizinhas também se aplica?\n", "| Grupo | n | Sim |", "|---|---|---|"]
    for g in ("isolado", "controle"):
        x = s[s["grupo"] == g]
        k, n = int((x["sugerido_se_aplica"] == "S").sum()), len(x)
        lo, hi = wilson(k, n)
        rel.append(f"| {g} | {n} | {k} ({k / n:.0%}; {lo:.0%} a {hi:.0%}) |" if n else f"| {g} | 0 | - |")
    x_iso = d[d["grupo"] == "isolado"]
    x_ctl = d[d["grupo"] == "controle"]
    if len(x_iso) and len(x_ctl):
        # teste exato de Fisher (unilateral: isolados têm mais P ou I) sem scipy
        a_ = int(x_iso["tema_adequado"].isin(["P", "I"]).sum()); b_ = len(x_iso) - a_
        c_ = int(x_ctl["tema_adequado"].isin(["P", "I"]).sum()); d_ = len(x_ctl) - c_
        n1, n2, m = a_ + b_, c_ + d_, a_ + c_
        tot = math.comb(n1 + n2, m)
        p = sum(math.comb(n1, i) * math.comb(n2, m - i) for i in range(a_, min(n1, m) + 1)) / tot
        rel += ["", f"Teste exato de Fisher (unilateral) para parcial ou inadequado, isolados contra controle: p = {p:.4f}."]
    (P / "fase4" / "inconsistencias_cedi.md").write_text("\n".join(rel), encoding="utf-8")
    print("\n".join(rel))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("amostrar")
    s1.add_argument("--base", type=Path, default=sorted(P.glob("base_fase2_*.parquet"))[-1])
    s1.add_argument("--temas", type=Path, default=P / "temas_long_20261027.parquet")
    s1.add_argument("--refazer", action="store_true")
    sub.add_parser("resumir")
    a = ap.parse_args()
    amostrar(a) if a.cmd == "amostrar" else resumir(a)


if __name__ == "__main__":
    main()
