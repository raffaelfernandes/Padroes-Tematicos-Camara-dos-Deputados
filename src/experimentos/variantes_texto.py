"""
variantes_texto.py

Experimento (branch exp/embedding-sem-formulas, 14/11/2026). Pergunta: tirar do texto do embedding
as palavras que já tiramos dos rótulos melhora os tópicos? A motivação é a leitura da Fase 3: o e5
formou um tópico genérico com milhares de ementas do tipo "Altera a Lei, para...".

Duas variantes do texto do embedding, aplicadas aos mesmos modelos (e5 e BERTimbau), para separar
os efeitos:
  semformulas  tira só as expressões e palavras de fórmula legislativa (altera, revoga, institui,
               dispõe sobre, dá nova redação, e dá outras providências, artigo, inciso...), preservando
               nomes de leis e mantendo as palavras gramaticais e a ordem;
  rotulos      aplica exatamente o pré-processamento dos rótulos (c-TF-IDF): minúsculas, só palavras
               com 3 letras ou mais, sem números, sem stopwords e sem as palavras de fórmula.
O texto_modelo (usado nos rótulos, no NPMI e na leitura) não muda; só a coluna texto_embedding.

Critério fixado antes de ver os resultados: mesma configuração do modelo principal (UMAP 30 vizinhos,
HDBSCAN mcs 100, eom, min_samples 10, reatribuição pelos 15 vizinhos), para isolar o efeito do texto.
Uma variante só substitui o modelo principal se superar o BERTimbau atual em precisão BCubed E na
fração de apensadas no mesmo tópico (que não depende do codTema), e se a leitura dos tópicos não
mostrar tópicos formados pela fórmula. Caso contrário, entra como análise de sensibilidade.

Subcomandos (a partir de code/):
    uv run python src/experimentos/variantes_texto.py gerar
    uv run python src/experimentos/variantes_texto.py avaliar
    uv run python src/experimentos/variantes_texto.py sementes --variante semformulas --modelos bertimbau e5
(os comandos de embeddings e clustering entre os dois estão no README da branch)

Saídas em data/processed/exp_texto/.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
sys.path.insert(0, "src/extras")
from fase3_clustering import STOP_PT, diversidade, npmi_medio, palavras_por_topico, vetorizador  # noqa: E402
from fase4_avaliacao import Gabarito  # noqa: E402

P = Path("data/processed")
EXP = P / "exp_texto"

# Variante "semformulas": expressões e palavras de fórmula legislativa. Usa as palavras de fórmula da lista
# dos rótulos (fase3_clustering.STOP_PT) que são verbos de alteração ou estrutura legal, mais "revoga" e as
# expressões fixas das ementas; ficam de fora as palavras genéricas da lista (nacional, federal, novo, forma...),
# que fazem parte de nomes como "Política Nacional de...". Nomes de leis ("Lei Maria da Penha",
# "Consolidação das Leis do Trabalho", "Lei de Diretrizes e Bases") são preservados.
EXPRESSOES = [
    r"e dá outras providências", r"dá outras providências", r"outras providências",
    r"dá nova redação (?:a|ao|à|aos|às)", r"dá nova redação", r"nova redação",
    r"dispõe sobre", r"dispor sobre", r"passam? a vigorar", r"com a seguinte redação",
    r"entra em vigor na data de sua publicação", r"entra em vigor", r"na data de sua publicação",
    r"decreto-lei", r"medida provisória",
]
FORMULAS = set("""art arts artigo artigos lei leis decreto dispõe dispor dispositivo dispositivos altera alterar
alterada alteradas alterado alterados acrescenta acrescentar acrescido acrescida inclui incluir institui instituir
estabelece estabelecer revoga revogar revogado revogada redação parágrafo parágrafos inciso incisos alínea alíneas
caput vigor vigorar publicação""".split())
# nome de lei: "Lei"/"Leis" seguido de palavra com maiúscula, direto ou depois de de/do/da/dos/das
_NOME_LEI = re.compile(r"\b(Leis?)(?=\s+(?:d[aeo]s?\s+)?[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
_EXP_RE = re.compile(r"(?<![\w-])(?:" + "|".join(EXPRESSOES) + r")(?![\w])", re.IGNORECASE)
_FORM_RE = re.compile(r"(?<![\w-])(?:" + "|".join(sorted(map(re.escape, FORMULAS), key=len, reverse=True)) + r")(?![\w])\.?",
                      re.IGNORECASE)
_FUNC = r"(?:a|o|as|os|ao|aos|à|às|de|do|da|dos|das|no|na|nos|nas|pelo|pela|pelos|pelas|e|ambos|ambas|que|em|único|referida|referido)"
TOKEN_ROTULO = re.compile(r"(?u)\b[^\W\d_]{3,}\b")


def sem_formulas(texto: str) -> str:
    """Tira as expressões e palavras de fórmula (sem diferenciar maiúsculas), preservando nomes de leis, e
    limpa o que sobra delas: artigos e preposições soltos antes de pontuação, hífens e pontos órfãos,
    vírgulas repetidas. O resto do texto fica como está, com a ordem e a gramática originais."""
    s = _NOME_LEI.sub(lambda m: m.group(1).replace("L", "\x00"), texto or "")   # protege nomes de leis
    s = _EXP_RE.sub(" ", s)
    s = _FORM_RE.sub(" ", s)
    s = s.replace("\x00", "L")
    s = re.sub(r"(?<=\s)[-–]+(?=\s)|(?<=\s)[-–]+$|^\s*[-–]+", " ", s)       # travessões e hífens órfãos
    s = re.sub(r"\s+", " ", s)
    for _ in range(4):                                                    # palavras gramaticais órfãs
        s = re.sub(r"(?i)\b" + _FUNC + r"\s*(?=[,.;:)–-]|$)", "", s)
        s = re.sub(r"(?i)^\s*(?:" + _FUNC + r"\b\s*|[,.;:–-]\s*)+", "", s)
        s = re.sub(r"\s+([,.;:)])", r"\1", s)
        s = re.sub(r"([,.;:])(?:\s*[,.;:–-])+", r"\1", s)
        s = re.sub(r"\(\s+", "(", s)
        s = re.sub(r"\(\s*\)", "", s)
        s = re.sub(r"\s+", " ", s)
    s = s.strip(" ,;:-–")
    return s[:1].upper() + s[1:] if s else s


def como_rotulos(texto: str) -> str:
    """O mesmo pré-processamento do vetorizador dos rótulos: minúsculas, palavras com 3+ letras, sem STOP_PT."""
    return " ".join(t for t in TOKEN_ROTULO.findall((texto or "").lower()) if t not in STOP_PT)


VARIANTES = {"semformulas": sem_formulas, "rotulos": como_rotulos}


def gerar(a) -> None:
    EXP.mkdir(parents=True, exist_ok=True)
    base = pd.read_parquet(a.base)
    data = a.base.stem.split("_")[-1]
    rel = ["# Variantes do texto do embedding\n", f"Base de origem: `{a.base.name}`.\n"]
    rng = np.random.default_rng(42)
    exemplos = base.drop_duplicates("id_texto_unico").sample(8, random_state=42)
    for nome, f in VARIANTES.items():
        b = base.copy()
        b["texto_embedding"] = b["texto_embedding"].fillna("").map(f)
        n_pal_antes = base["texto_embedding"].fillna("").str.split().str.len()
        n_pal_depois = b["texto_embedding"].str.split().str.len()
        vazios = int((n_pal_depois == 0).sum())
        destino = EXP / f"base_fase2_{nome}_{data}.parquet"
        b.to_parquet(destino, index=False)
        u_antes = base.drop_duplicates("id_texto_unico")["texto_embedding"].nunique()
        u_depois = b.drop_duplicates("id_texto_unico")["texto_embedding"].nunique()
        rel += [f"## {nome}\n",
                f"Arquivo: `{destino}`. Palavras por texto: mediana de {n_pal_antes.median():.0f} antes e "
                f"{n_pal_depois.median():.0f} depois. Textos vazios depois: {vazios}. Textos distintos: "
                f"{u_antes} antes e {u_depois} depois (textos que ficaram iguais continuam com id próprio).\n",
                "| antes | depois |", "|---|---|"]
        for i in exemplos.index:
            rel.append(f"| {base.at[i, 'texto_embedding'][:160]} | {b.at[i, 'texto_embedding'][:160]} |")
        rel.append("")
        print(f"{nome}: {destino} (vazios: {vazios})")
    (EXP / "variantes.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {EXP / 'variantes.md'}")


def avaliar(a) -> None:
    from leis_citadas import primeira_lei
    base = pd.read_parquet(a.base, columns=["id", "id_texto_unico", "texto_modelo", "eh_formulaica", "idPropPrincipal", "ementa"])
    temas = pd.read_parquet(P / "temas_long_20261027.parquet")
    conj = temas.groupby("id")["codTema"].apply(lambda s: frozenset(int(x) for x in s))
    tem = base["id"].map(conj)
    ok = tem.notna().to_numpy()
    gab = Gabarito(list(tem[ok]))
    ids = base["id"].to_numpy()
    pos_id = pd.Series(np.arange(len(base)), index=ids)
    pr = base.dropna(subset=["idPropPrincipal"])
    pr = pr[pr["idPropPrincipal"].astype("int64").isin(ids)]
    ia = pos_id.loc[pr["id"]].to_numpy()
    ib = pos_id.loc[pr["idPropPrincipal"].astype("int64")].to_numpy()
    lei = base["ementa"].map(primeira_lei)
    sem_lei = (lei.isna() & tem.notna()).to_numpy()
    gab_sl = Gabarito(list(tem[sem_lei]))
    tema_long = temas[["id", "tema"]]
    # NPMI e diversidade sobre os textos únicos substantivos, com o vetorizador dos rótulos (como na Fase 3)
    u = base.drop_duplicates("id_texto_unico").sort_values("id_texto_unico").reset_index(drop=True)
    form_u = base.groupby("id_texto_unico")["eh_formulaica"].all().reindex(u["id_texto_unico"]).to_numpy()
    fit = np.nonzero(~form_u)[0]
    vec = vetorizador()
    X = vec.fit_transform(u["texto_modelo"].fillna("").iloc[fit]).tocsr()
    vocab = vec.get_feature_names_out()
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    Xb = (X > 0).astype(np.float32).tocsc()
    pos_u = pd.Series(np.arange(len(u)), index=u["id_texto_unico"])

    candidatos = {
        "BERTimbau (texto atual, modelo principal)": P / "fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet",
        "e5 (texto atual)": P / "fase3/topicos_e5_nn30_mcs100_eom_ms10_rk.parquet",
    }
    for var in VARIANTES:
        for m in ("e5", "bertimbau"):
            f = EXP / f"fase3_{var}" / f"topicos_{m}_nn30_mcs100_eom_ms10_rk.parquet"
            if f.exists():
                candidatos[f"{'BERTimbau' if m == 'bertimbau' else 'e5'} ({var})"] = f
    rng = np.random.default_rng(130)
    linhas = []
    for nome, f in candidatos.items():
        t = pd.read_parquet(f)
        lab = t.set_index("id")["topico_alt_ctfidf"].reindex(ids).to_numpy()
        r = gab.bcubed(lab[ok])
        ale = [gab.bcubed(rng.permutation(lab[ok])) for _ in range(3)]
        p_ale, r_ale = np.mean([x["P"] for x in ale]), np.mean([x["R"] for x in ale])
        lab_u = np.full(len(u), -1)
        lab_u[pos_u.loc[base["id_texto_unico"]].to_numpy()] = lab
        pal = palavras_por_topico(X, lab_u[fit], vocab)
        tam = pd.Series(lab).value_counts(normalize=True)
        # tópicos "pega-tudo": pureza pelo tema oficial mais comum; o e5 com o texto atual tem um tópico de
        # 3.974 proposições com pureza de 31% e termos genéricos
        tt = pd.DataFrame({"id": ids, "t": lab})
        n_t = tt.groupby("t").size()
        pureza = tema_long.merge(tt, on="id").groupby("t")["tema"].agg(lambda x: x.value_counts().iloc[0]) / n_t
        maior = n_t.idxmax()
        linhas.append({
            "versao": nome, "topicos": int(pd.Series(lab).nunique()),
            "outliers_hdbscan": round(float((t["origem_topico"] == "reduce_outliers").sum()
                                            / t["origem_topico"].isin(["hdbscan", "reduce_outliers"]).sum()), 3),
            "P": round(r["P"], 3), "R": round(r["R"], 3), "F": round(r["F"], 3),
            "P_sobre_acaso": round(r["P"] / p_ale, 2), "R_sobre_acaso": round(r["R"] / r_ale, 2),
            "apensadas": round(float((lab[ia] == lab[ib]).mean()), 3),
            "P_sem_lei_citada": round(gab_sl.bcubed(lab[sem_lei])["P"], 3),
            "npmi": round(npmi_medio(Xb, pal, vocab_idx), 3), "diversidade": round(diversidade(pal), 3),
            "maior_topico": round(float(tam.iloc[0]), 3),
            "pureza_maior_topico": round(float(pureza[maior]), 2),
            "props_em_topicos_pureza_abaixo_40": round(float(n_t[pureza < 0.40].sum() / len(lab)), 3),
        })
        print(linhas[-1], flush=True)
    res = pd.DataFrame(linhas)
    res.to_csv(EXP / "avaliacao.csv", index=False)
    rel = ["# Variantes do texto do embedding: avaliação\n",
           "Mesma configuração para todos (UMAP 30 vizinhos, HDBSCAN mcs 100, eom, min_samples 10, "
           "reatribuição pelos 15 vizinhos; formulaicas pelo c-TF-IDF). P/R: BCubed estendido contra o codTema; "
           "`_sobre_acaso`: dividido pelo aleatório com os mesmos tamanhos; `apensadas`: pares de apensada e "
           "principal no mesmo tópico; `P_sem_lei_citada`: precisão só nas ementas que não citam lei; "
           "`pureza_maior_topico` e `props_em_topicos_pureza_abaixo_40`: sinal de tópico pega-tudo, como o maior "
           "tópico do e5 com o texto atual (3.974 proposições, pureza de 31%, termos genéricos).\n",
           "Critério fixado antes: a variante substitui o modelo principal só se superar o BERTimbau atual em P e "
           "em apensadas, sem tópico pega-tudo na leitura.\n", res.to_markdown(index=False)]
    (EXP / "avaliacao.md").write_text("\n".join(rel), encoding="utf-8")
    print(f"Relatório: {EXP / 'avaliacao.md'}")


def sementes(a) -> None:
    """Refaz UMAP, HDBSCAN e reatribuição com outras sementes do UMAP para uma variante, com a mesma rotina
    de src/extras/robustez_modelos.py (formulaicas pelo centroide). Compara com
    data/processed/fase4/robustez/sementes.csv, que tem o texto atual."""
    import robustez_modelos as rm
    rm.BASE = EXP / f"base_fase2_{a.variante}_{a.base.stem.split('_')[-1]}.parquet"
    rm.EMB = EXP / f"emb_{a.variante}"
    rm.FASE3 = EXP / f"fase3_{a.variante}"
    rm.SAIDA = EXP / f"sementes_{a.variante}"
    rm.sementes(argparse.Namespace(modelos=a.modelos, sementes=a.sementes))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("gerar", "avaliar", "sementes"):
        s = sub.add_parser(nome)
        s.add_argument("--base", type=Path, default=P / "base_fase2_20261101.parquet")
        if nome == "sementes":
            s.add_argument("--variante", choices=list(VARIANTES), default="semformulas")
            s.add_argument("--modelos", nargs="+", default=["bertimbau"])
            s.add_argument("--sementes", nargs="+", type=int, default=[42, 1, 2, 3, 4])
    a = ap.parse_args()
    {"gerar": gerar, "avaliar": avaliar, "sementes": sementes}[a.cmd](a)


if __name__ == "__main__":
    main()
