"""
figura_topicos_temas.py

Extra da revisão final do TCC (14/11/2026). Heatmap dos 20 maiores tópicos do modelo principal contra
os temas oficiais: cada célula é a fração das proposições do tópico que têm aquele tema (o codTema é
multirrótulo, então uma linha pode somar mais de 100%). Mostra de uma vez a pureza (uma célula forte por
linha), a fragmentação (um tema forte em várias linhas) e os tópicos transversais (várias células médias).

Mostra os 15 maiores tópicos e os temas que chegam a 20% em algum deles.

Uso (a partir de code/):
    uv run python src/extras/figura_topicos_temas.py
Saída: outputs/figs/fig_topicos_temas.pdf e .png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

sys.path.insert(0, "src")
from fase5_figuras import ROTULOS  # noqa: E402

P = Path("data/processed")
SAIDA = Path("outputs/figs")
N_TOP = 15
LIMIAR_COL = 0.20   # tema entra como coluna se chega a 20% em algum dos tópicos mostrados
CURTO = {
    "Administração Pública": "Adm. Pública",
    "Agricultura, Pecuária, Pesca e Extrativismo": "Agricultura",
    "Arte, Cultura e Religião": "Cultura",
    "Cidades e Desenvolvimento Urbano": "Cidades",
    "Ciência, Tecnologia e Inovação": "C&T e Inovação",
    "Comunicações": "Comunicações",
    "Defesa e Segurança": "Defesa e Seg.",
    "Direito Civil e Processual Civil": "Dir. Civil",
    "Direito Constitucional": "Dir. Constitucional",
    "Direito Penal e Processual Penal": "Dir. Penal",
    "Direito e Justiça": "Direito e Justiça",
    "Direito e Defesa do Consumidor": "Consumidor",
    "Direitos Humanos e Minorias": "Dir. Humanos",
    "Economia": "Economia",
    "Educação": "Educação",
    "Energia, Recursos Hídricos e Minerais": "Energia",
    "Esporte e Lazer": "Esporte",
    "Finanças Públicas e Orçamento": "Finanças Públicas",
    "Homenagens e Datas Comemorativas": "Homenagens",
    "Indústria, Comércio e Serviços": "Indústria e Com.",
    "Meio Ambiente e Desenvolvimento Sustentável": "Meio Ambiente",
    "Previdência e Assistência Social": "Previdência",
    "Processo Legislativo e Atuação Parlamentar": "Proc. Legislativo",
    "Saúde": "Saúde",
    "Trabalho e Emprego": "Trabalho",
    "Viação, Transporte e Mobilidade": "Transporte",
    "Política, Partidos e Eleições": "Política",
    "Relações Internacionais e Comércio Exterior": "Rel. Internacionais",
    "Turismo": "Turismo",
    "Estrutura Fundiária": "Estr. Fundiária",
    "Ciências Exatas e da Terra": "C. Exatas",
    "Ciências Sociais e Humanas": "C. Sociais",
}
# rampa sequencial azul (um matiz, claro -> escuro), com branco no zero
RAMPA = ["#ffffff", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def main() -> None:
    t = pd.read_parquet(P / "fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet")[["id", "topico_alt_ctfidf"]]
    te = pd.read_parquet(P / "temas_long_20261027.parquet")[["id", "tema"]]
    d = t.merge(te, on="id")
    n_top = t.groupby("topico_alt_ctfidf").size()
    tops = n_top.sort_values(ascending=False).head(N_TOP).index
    m = pd.crosstab(d["topico_alt_ctfidf"], d["tema"]).reindex(tops)
    frac = m.div(n_top.reindex(tops), axis=0)
    cols = frac.columns[(frac >= LIMIAR_COL).any()]
    frac = frac[cols]
    # ordena colunas pelo primeiro tópico em que o tema é o dominante (deixa a "diagonal" visível)
    dom = frac.idxmax(axis=1)
    ordem = list(dict.fromkeys(dom.tolist())) + [c for c in frac.sum().sort_values(ascending=False).index if c not in set(dom)]
    frac = frac[ordem]
    rot_lin = [f"{ROTULOS.get(k, k)} ({n_top[k]:,})".replace(f"({n_top[k]:,})", "(" + f"{n_top[k]:,}".replace(",", ".") + ")") for k in frac.index]
    rot_col = [CURTO.get(c, c) for c in frac.columns]

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    # tamanho real de impressão (largura do texto do template SBC, cerca de 16 cm): fontes de 8 pt no PDF
    fig, ax = plt.subplots(figsize=(6.3, 4.0))
    cmap = LinearSegmentedColormap.from_list("azul", RAMPA)
    im = ax.imshow(frac.to_numpy(), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(rot_col)), rot_col, rotation=50, ha="right", rotation_mode="anchor", fontsize=8)
    ax.set_yticks(range(len(rot_lin)), rot_lin, fontsize=8)
    ax.tick_params(length=0)
    # espaçador de 2px entre células
    ax.set_xticks(np.arange(-0.5, len(rot_col), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rot_lin), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    # rótulos só nas células fortes (>= 30%)
    v = frac.to_numpy()
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            if v[i, j] >= 0.30:
                ax.text(j, i, f"{v[i, j] * 100:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if v[i, j] >= 0.55 else "#1f2328")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("% das proposições do tópico", fontsize=8)
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0], labels=["0", "25", "50", "75", "100"])
    cb.ax.tick_params(labelsize=8, length=0)
    cb.outline.set_visible(False)
    fig.tight_layout()
    SAIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA / "fig_topicos_temas.pdf", bbox_inches="tight", pad_inches=0.15)
    fig.savefig(SAIDA / "fig_topicos_temas.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    print(f"Figura: {SAIDA / 'fig_topicos_temas.pdf'} ({len(rot_lin)} tópicos x {len(rot_col)} temas)")


if __name__ == "__main__":
    main()
