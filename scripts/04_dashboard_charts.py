"""04_dashboard_charts.py — gera os gráficos do dashboard HTML a partir de output/.

Gráficos:
  yield.png        Yield líquido por perfil (base 35%)
  preco_noite.png  Preço médio/noite projetado por perfil
  cpm2.png         Custo R$/m² de compra por bairro
  demanda.png      Demanda (reviews/ano) e risco de vacância por bairro
  receita.png      Receita líquida anual vs preço de compra (bolhas)
  payoff.png       Histórico de yield por cenário para Morretes 3q

Execução: python scripts/04_dashboard_charts.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dashboard", "graficos")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"font.family": "sans-serif",
                     "axes.edgecolor": "#DCE3EF", "axes.linewidth": 1,
                     "figure.facecolor": "white", "axes.facecolor": "white"})
NAVY = "#00143D"; AZUL = "#0055FF"; CORAL = "#FC6058"
GREEN = "#16a34a"; GRAY = "#9ca3af"


def bar(ax, labels, values, colors, title, fmt=".1f", ylabel=""):
    bars = ax.bar(labels, values, color=colors, zorder=3)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + (max(values) * 0.01),
                fmt.format(v), ha="center", va="bottom", fontsize=9, color="#0E1B33")
    ax.set_title(title, fontsize=13, color=NAVY, weight="bold", loc="left", pad=14)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color="#EEF2F9", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)


def main():
    yd = pd.read_csv(os.path.join(ROOT, "output", "yield", "yield_profiles.csv"))
    base = yd[yd["cenario"] == "base"].copy()
    dem = pd.read_csv(os.path.join(ROOT, "output", "revenue", "demand_market.csv"))
    rev = pd.read_csv(os.path.join(ROOT, "output", "revenue", "scenarios.csv"))

    # 1 ---- Yield por perfil (ordenado)
    b = base.sort_values("yield_liquido", ascending=False).reset_index(drop=True)
    labels = [f"{r['suburb']}\n{r['beds_group']}" for _, r in b.iterrows()][:8]
    vals = (b["yield_liquido"] * 100)[:8].round(2)
    colors = [GREEN if v == vals.max() else (CORAL if "Centro" in l else AZUL)
              for v, l in zip(vals, labels)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bar(ax, labels, vals, colors, "Yield líquido ao ano por perfil (%) — cenário base (35% ocupação)", ylabel="%")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "yield.png"), dpi=150); plt.close(fig)

    # 2 ---- Preço/noite projetado
    p = pd.read_csv(os.path.join(ROOT, "output", "revenue", "price_by_profile.csv"))
    p = p.sort_values("preco_anual_proj", ascending=False).head(8)
    labels = [f"{r['suburb']}\n{r['beds_group']}" for _, r in p.iterrows()]
    vals = p["preco_anual_proj"].round(0)
    colors = [AZUL] * len(vals); colors[labels.index([l for l in labels if "Morretes" in l][0])] = GREEN
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.yaxis.set_major_formatter(lambda x, _: f"R$ {x:,.0f}" if abs(x) < 1000000 else f"R$ {x/1000:.0f}k")
    bar(ax, labels, vals, colors, "Preço médio por noite projetado (anual) por perfil", ylabel="R$")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "preco_noite.png"), dpi=150); plt.close(fig)

    # 3 ---- Custo R$/m² compra por bairro (relevantes)
    compra = pd.read_csv(os.path.join(ROOT, "output", "yield", "compra_perfil.csv"))
    c = compra[(compra["suburb"].isin(["Morretes", "Centro", "Meia Praia", "Casa Branca",
                                       "Tabuleiro dos Oliveiras"])) &
               compra["beds_group"].isin(["2 quartos", "3 quartos"])]
    c = c.groupby("suburb", as_index=False)["med_m2"].median().sort_values("med_m2")
    labels = c["suburb"]; vals = c["med_m2"].round(0)
    colors = [GREEN if l == "Morretes" else CORAL if l == "Centro" else AZUL for l in labels]
    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.yaxis.set_major_formatter(lambda x, _: f"R$ {x:,.0f}")
    bar(ax, labels, vals, colors, "Custo de compra (R$/m²) por bairro — aptos 2–3 quartos", ylabel="R$/m²")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "cpm2.png"), dpi=150); plt.close(fig)

    # 4 ---- Demanda (reviews/ano) + risco vacância
    relevant = ["Morretes", "Meia Praia", "Centro"]
    d = dem[dem["suburb"].isin(relevant)].copy()
    d = d.set_index("suburb")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(d))
    w = 0.4
    cols = [GREEN if i == "Morretes" else (CORAL if i == "Centro" else AZUL) for i in d.index]
    ax.bar(x - w/2, d["reviews_por_ano"], w, color=cols, label="Demanda (reviews/ano)", zorder=3)
    ax2 = ax.twinx()
    ax2.bar(x + w/2, d["share_zero_reviews"] * 100, w, color=GRAY,
            label="Risco de vacância (% sem reviews)", zorder=3, alpha=0.85)
    for i, v in enumerate(d["reviews_por_ano"]):
        ax.text(i - w/2, v + 0.2, f"{v:.1f}", ha="center", fontsize=9)
    for i, v in enumerate(d["share_zero_reviews"] * 100):
        ax2.text(i + w/2, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9, color="#4B5563")
    ax.set_xticks(x); ax.set_xticklabels(d.index)
    ax.set_ylabel("Demanda (reviews/ano)", color=NAVY)
    ax2.set_ylabel("Risco de vacância (%)", color=GRAY)
    ax.set_title("Demanda relativa e risco de vacância por bairro", fontsize=13, color=NAVY, weight="bold", loc="left", pad=14)
    ax.yaxis.grid(True, color="#EEF2F9", zorder=0); ax.set_axisbelow(True)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "demanda.png"), dpi=150); plt.close(fig)

    # 5 ---- Receita líquida vs preço de compra (bolhas)
    b2 = base.copy()
    b2 = b2.groupby(["suburb", "beds_group"], as_index=False).agg(
        preco_compra=("preco_compra", "first"), receita_liq=("receita_liquida", "first"),
        yield_liq=("yield_liquido", "first"))
    b2 = b2[b2["preco_compra"] > 0]
    fig, ax = plt.subplots(figsize=(8, 5))
    yy = (b2["yield_liq"] * 100).round(2)
    sz = b2["receita_liq"] / 500
    for _, r in b2.iterrows():
        col = GREEN if (r["suburb"] == "Morretes" and r["beds_group"] in ["2 quartos", "3 quartos"]) \
              else CORAL if r["suburb"] == "Centro" else AZUL
        ax.scatter(r["preco_compra"] / 1e6, r["yield_liq"] * 100, s=r["receita_liq"] / 400,
                   color=col, alpha=0.75, edgecolor="white", zorder=3)
        ax.annotate(f"{r['suburb']} {r['beds_group']}",
                    (r["preco_compra"] / 1e6, r["yield_liq"] * 100),
                    fontsize=8, color="#0E1B33", ha="center", va="bottom")
    ax.axhline(6, color=GRAY, ls="--", lw=1)
    ax.text(0.02, 6.05, "meta de yield 6%", color=GRAY, fontsize=8, va="bottom")
    ax.set_xlabel("Preço de compra (R$ milhões)"); ax.set_ylabel("Yield líquido (%)")
    ax.set_title("Yield vs Preço de compra (tamanho da bolha = receita anual)", fontsize=13, color=NAVY, weight="bold", loc="left", pad=14)
    ax.xaxis.set_major_formatter(lambda x, _: f"R$ {x:.0f}M")
    ax.yaxis.grid(True, color="#EEF2F9", zorder=0); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "bolhas.png"), dpi=150); plt.close(fig)

    # 6 ---- Payoff Morretes 3q por cenário
    sel = rev[(rev["suburb"] == "Morretes") & (rev["beds_group"] == "3 quartos")]
    cen = ["conservador", "base", "otimista"]; occ = [0.25, 0.35, 0.45]
    bruta = [sel[sel["cenario"] == c]["receita_anual_bruta"].iloc[0] for c in cen]
    liquida = [b * 0.85 - 4050 for b in bruta]  # 15% gestão + fixo
    preco = 845000.0
    yields_ = [l / preco * 100 for l in liquida]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = [CORAL, AZUL, GREEN]
    bars = ax.bar([f"{o:.0%} ocupação" for o in occ], yields_, color=colors, zorder=3)
    for b, y, liq in zip(bars, yields_, liquida):
        ax.text(b.get_x() + b.get_width()/2, y + 0.4, f"{y:.1f}%\nR$ {liq:,.0f}/ano",
                ha="center", va="bottom", fontsize=9)
    ax.axhline(6, color=GRAY, ls="--", lw=1); ax.text(0.002, 6.1, "meta 6%", color=GRAY, fontsize=8)
    ax.set_title("Morretes 3 quartos (~R$ 845 mil) — yield por cenário de ocupação",
                 fontsize=13, color=NAVY, weight="bold", loc="left", pad=14)
    ax.set_ylabel("Yield líquido (%)"); ax.yaxis.grid(True, color="#EEF2F9", zorder=0); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "payoff.png"), dpi=150); plt.close(fig)

    print("Gráficos gerados em dashboard/graficos/")
    for f in sorted(os.listdir(OUT)):
        print(" -", f)


if __name__ == "__main__":
    main()