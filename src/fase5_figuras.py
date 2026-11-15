"""
fase5_figuras.py

Figuras da Fase 5 para a monografia (PDF vetorial para o LaTeX e PNG para conferir).
Lê as saídas do src/fase5_rqs.py, versão "todas".

    fig_rq1_series.pdf        série mensal de seis tópicos, com as janelas pré-eleitorais
    fig_rq1_razoes.pdf        razão janela/controle em 2022 contra 2026, um ponto por tópico
    fig_rq2_heatmap_leg56.pdf partido x tópico, log-odds (z) com peso limitado, 56ª legislatura
    fig_rq2_heatmap_leg57.pdf idem, 57ª legislatura

Uso (a partir de code/; precisa do matplotlib: uv add matplotlib):
    uv run python src/fase5_figuras.py

Os rótulos curtos dos tópicos (ROTULOS) foram escritos à mão (refeitos em 15/11/2026 para a versão sem fórmulas) a partir dos termos do c-TF-IDF
e das ementas representativas de cada tópico. Eles só servem para as figuras.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROTULOS = {
    0: "COVID e calamidade pública", 1: "Código Penal: crimes e penas", 2: "SUS",
    3: "Código Civil e de Processo Civil", 4: "Datas comemorativas", 5: "CLT e relações de trabalho",
    6: "Código de Trânsito", 7: "LDB e educação básica", 8: "Imposto de Renda",
    9: "Segurança pública e polícias", 10: "Violência doméstica", 11: "Títulos de capital nacional",
    12: "Previdência Social", 13: "Regulamentação de profissões", 14: "Finanças públicas e repasses",
    15: "Patrimônio cultural imaterial", 16: "Energia elétrica", 17: "Programas de desenvolvimento e inovação",
    18: "Terras, mineração e meio ambiente", 19: "Animais domésticos", 20: "Transporte e mobilidade urbana",
    21: "Eleições e partidos", 22: "Autismo (TEA)", 23: "Isenção de IPI", 24: "Defesa do consumidor",
    25: "Pessoa com deficiência", 26: "Ensino superior e estudantes", 27: "BPC e Bolsa Família",
    28: "Internet, dados e IA", 29: "Denominação de rodovias", 30: "Planos de saúde",
    31: "Obrigações a estabelecimentos", 32: "Licitações e administração", 33: "Execução penal",
    34: "Armas de fogo", 35: "Alimentos, bebidas e rotulagem", 36: "Apostas e loterias", 37: "Aviação",
    38: "Heróis e Heroínas da Pátria", 39: "Esporte", 40: "Prevenção à violência",
    41: "Código de Processo Penal", 42: "Universidades e campi", 43: "Pessoa idosa",
    44: "Micro e pequenas empresas", 45: "PIS/Cofins", 46: "Resíduos sólidos", 47: "Petróleo e gás",
    48: "Ambiente digital e crianças", 49: "ECA", 50: "Maus-tratos a animais", 51: "Telefonia",
    52: "FGTS", 53: "Desastres e defesa civil", 54: "Saneamento e água", 55: "Minha Casa, Minha Vida",
    56: "Concursos públicos", 57: "Normas para os entes federativos", 58: "Selos e programas nacionais",
    59: "Infraestrutura de telecomunicações", 60: "Código Tributário", 61: "Instituições financeiras",
    62: "Radiodifusão", 63: "Rodovias e pedágios", 64: "Terrorismo e organizações criminosas",
    65: "Crimes ambientais", 66: "Improbidade administrativa",
}
SERIES_TOPICOS = [30, 0, 53, 10, 54, 21]

AZUL, LARANJA, CINZA, CINZA_CLARO = "#2a78d6", "#eb6834", "#8a8984", "#d9d8d3"
TINTA, TINTA2 = "#0b0b0b", "#52514e"
ELEICOES = [pd.Timestamp("2022-10-02"), pd.Timestamp("2026-10-04")]
JANELAS = [(pd.Timestamp("2022-04-01"), pd.Timestamp("2022-09-30")), (pd.Timestamp("2026-04-01"), pd.Timestamp("2026-09-30"))]
MIN_ATIVOS = 30   # meses de recesso (janeiro) têm poucos deputados ativos e ficam de fora da série


def estilo() -> None:
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "TeX Gyre Termes", "DejaVu Serif"],
        "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.edgecolor": CINZA, "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#ecebe7",
        "grid.linewidth": 0.6, "axes.axisbelow": True, "pdf.fonttype": 42, "savefig.dpi": 200,
    })


def salva(fig, pasta: Path, nome: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(pasta / f"{nome}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"  {nome}.pdf")


# ---------------------------------------------------------------- RQ1
def fig_series(serie: pd.DataFrame, pasta: Path) -> None:
    s = serie[serie["ativos"] >= MIN_ATIVOS].copy()
    s["data"] = pd.to_datetime(s["ym"]) + pd.Timedelta(days=14)
    meses = s[["data"]].drop_duplicates().sort_values("data")
    fig, axs = plt.subplots(2, 3, figsize=(6.5, 3.9), sharex=True)
    for ax, t in zip(axs.ravel(), SERIES_TOPICOS):
        x = meses.merge(s[s["topico"] == t][["data", "taxa_deputados"]], on="data", how="left").fillna(0)
        for a, b in JANELAS:
            ax.axvspan(a, b, color="#f0efec", lw=0, zorder=0)
        for e in ELEICOES:
            ax.axvline(e, color=CINZA, lw=0.8, ls=(0, (3, 2)), zorder=1)
        ax.plot(x["data"], x["taxa_deputados"] * 100, color=AZUL, lw=1.4, zorder=2)
        ax.set_title(ROTULOS[t], loc="left", color=TINTA, fontsize=9)
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(2))
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
        if t == 30:   # planos de saúde
            pico = x.loc[x["taxa_deputados"].idxmax()]
            ax.annotate("jun/2022: decisão do STJ\nsobre o rol da ANS", xy=(pico["data"], pico["taxa_deputados"] * 100),
                        xytext=(pd.Timestamp("2023-02-01"), pico["taxa_deputados"] * 100 * 0.62), fontsize=7, color=TINTA2,
                        arrowprops={"arrowstyle": "-", "color": CINZA, "lw": 0.7})
    for ax in axs[:, 0]:
        ax.set_ylabel("% dos deputados ativos")
    fig.text(0.01, -0.06, "Fração dos deputados com proposição no mês que apresentaram ao menos uma sobre o tópico. "
             "\nFaixas cinza: abril a setembro de 2022 e 2026. Linhas tracejadas: eleições gerais.",
             fontsize=7.5, color=TINTA2)
    fig.tight_layout(h_pad=1.2, w_pad=1.0)
    salva(fig, pasta, "fig_rq1_series")


def fig_razoes(rq1: pd.DataFrame, pasta: Path) -> None:
    r = rq1.copy()
    for c in ("razao_2022", "razao_2026"):
        r[c] = r[c].clip(0.1, 10)
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    ax.set_xscale("log"); ax.set_yscale("log")
    lim = (0.15, 6.5)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.axhline(1, color=CINZA, lw=0.8); ax.axvline(1, color=CINZA, lw=0.8)
    for txt, (x, y), ha in [("sobe nas duas", (5.8, 5.8), "right"), ("cai nas duas", (0.17, 0.17), "left")]:
        ax.text(x, y, txt, fontsize=7.5, color=TINTA2, ha=ha, va="top" if y > 1 else "bottom", style="italic")
    base = r[r["padrao"] == "estável"]
    ax.scatter(base["razao_2022"], base["razao_2026"], s=16, color=CINZA_CLARO, edgecolor=CINZA, lw=0.5, zorder=2,
               label="sem mudança significativa")
    sob = r[r["padrao"].str.startswith("sobe")]
    cai = r[r["padrao"].str.startswith("cai")]
    ax.scatter(sob["razao_2022"], sob["razao_2026"], s=34, color=LARANJA, edgecolor="white", lw=1, zorder=3,
               label="sobe em uma eleição (p ajustado < 0,05)")
    ax.scatter(cai["razao_2022"], cai["razao_2026"], s=34, color=AZUL, edgecolor="white", lw=1, zorder=3,
               label="cai em uma eleição (p ajustado < 0,05)")
    for row in pd.concat([sob, cai]).itertuples():
        ax.annotate(ROTULOS[row.topico], (row.razao_2022, row.razao_2026), xytext=(6, -3), textcoords="offset points",
                    fontsize=7.5, color=TINTA)
    ticks = [0.25, 0.5, 1, 2, 4]
    ax.set_xticks(ticks); ax.set_yticks(ticks)
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("razão 2022 (abr–set 2022 / abr–set 2021)")
    ax.set_ylabel("razão 2026 (abr–set 2026 / abr–set 2025)")
    ax.legend(loc="upper left", fontsize=7, frameon=False, handletextpad=0.3)
    ax.set_aspect("equal")
    fig.tight_layout()
    salva(fig, pasta, "fig_rq1_razoes")


# ---------------------------------------------------------------- RQ2
def ordem_hierarquica(M: np.ndarray) -> np.ndarray:
    try:
        from scipy.cluster.hierarchy import leaves_list, linkage
        return leaves_list(linkage(M, method="average", metric="euclidean")) if len(M) > 2 else np.arange(len(M))
    except ImportError:
        return np.argsort(-M.max(1))


def fig_heatmap(rq2: pd.DataFrame, leg: int, pasta: Path) -> None:
    r = rq2.copy()
    r["assinatura"] = r["assinatura"].fillna("")
    cols = sorted(r.loc[r["assinatura"] != "", "topico"].unique())
    Z = r.pivot(index="partido", columns="topico", values="z_limitado")[cols]
    A = r.pivot(index="partido", columns="topico", values="assinatura")[cols]
    ro = Z.index[ordem_hierarquica(Z.to_numpy())]
    co = Z.columns[ordem_hierarquica(Z.to_numpy().T)]
    Z, A = Z.loc[ro, co], A.loc[ro, co]
    LIM = 6
    cmap = LinearSegmentedColormap.from_list("div", [AZUL, "#f0efec", LARANJA])
    w = max(4.5, 0.27 * len(co) + 1.6)
    h = max(3.0, 0.24 * len(ro) + 1.9)
    fig, ax = plt.subplots(figsize=(w, h))
    im = ax.imshow(Z.clip(-LIM, LIM).to_numpy(), cmap=cmap, vmin=-LIM, vmax=LIM, aspect="auto")
    ax.set_xticks(range(len(co)))
    ax.set_xticklabels([ROTULOS[c] for c in co], rotation=55, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(ro)))
    tam = r.drop_duplicates("partido").set_index("partido")["n_partido"]
    ax.set_yticklabels([f"{p} ({tam[p]})" for p in ro], fontsize=7.5)
    ax.grid(False)
    ax.set_xticks(np.arange(-0.5, len(co)), minor=True); ax.set_yticks(np.arange(-0.5, len(ro)), minor=True)
    ax.grid(which="minor", color="white", lw=1.2); ax.tick_params(which="minor", length=0)
    for i in range(len(ro)):
        for j in range(len(co)):
            a = A.iat[i, j]
            if a:
                cor = "white" if abs(Z.iat[i, j]) > 3.5 else TINTA
                ax.scatter(j, i, s=14, marker="o", lw=0.9, edgecolor=cor,
                           facecolor=cor if a == "partidária" else "none", zorder=3)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("log-odds (z), partido contra o resto", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    cb.outline.set_visible(False)
    ax.set_title(f"{leg}ª legislatura (entre parênteses, proposições do partido)", loc="left", fontsize=9, color=TINTA)
    from matplotlib.lines import Line2D
    mk = dict(marker="o", ls="none", markersize=4, markeredgecolor=TINTA)
    fig.legend(handles=[Line2D([], [], markerfacecolor=TINTA, label="assinatura partidária", **mk),
                        Line2D([], [], markerfacecolor="none",
                               label="assinatura individual (menos de 3 deputados ou um com mais de 50%)", **mk)],
               loc="upper left", bbox_to_anchor=(0.0, 0.0), ncol=2, frameon=False, fontsize=7, handletextpad=0.3)
    fig.tight_layout()
    salva(fig, pasta, f"fig_rq2_heatmap_leg{leg}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", default="data/processed/fase5", type=Path)
    ap.add_argument("--saida", default="outputs/figs", type=Path)
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    estilo()
    print(f"Figuras em {a.saida}:")
    fig_series(pd.read_csv(a.entrada / "rq1_serie_mensal_todas.csv"), a.saida)
    fig_razoes(pd.read_csv(a.entrada / "rq1_todas.csv"), a.saida)
    for leg in (56, 57):
        fig_heatmap(pd.read_csv(a.entrada / f"rq2_todas_leg{leg}.csv"), leg, a.saida)


if __name__ == "__main__":
    main()
