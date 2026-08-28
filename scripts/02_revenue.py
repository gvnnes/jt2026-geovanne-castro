"""02_revenue.py — Modelo de receita Airbnb por perfil produto.

Etapas:
 1. Preço médio/noite observado por (bairro x tipologia x nº quartos) em jan-abr/2025.
 2. Calibração da sazonalidade anual (índice mensal ancorado nos 4 meses observados)
    para converter preço médio observado -> preço médio anual.
 3. Índice de demanda corrigido: reviews / anos-host (proxy de idade real do imóvel)
    e metrica de competição: % de listings com 0 reviews por bairro.
 4. Receita anual por cenário de ocupação (25% / 35% / 45% das noites do ano).

Gera: output/revenue/price_by_profile.csv, demand_market.csv, scenarios.csv
Execução: python scripts/02_revenue.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np

from common import load_price, load_mesh, load_details, load_hosts

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "revenue")
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------- sazonalidade
# Índice mensal de preço (>=1 no pico). Jan-Abr ancorados nos dados; demais meses
# seguem padrão típico de cidade litorânea de SC (pico dezembro-fevereiro,
# fundo inverno ~maio-agosto).
MONTHLY_INDEX = {  # jan..dez
    1: 1.00, 2: 0.875, 3: 0.718, 4: 0.60, 5: 0.60, 6: 0.55,
    7: 0.55, 8: 0.55, 9: 0.60, 10: 0.65, 11: 0.75, 12: 1.05,
}
OCCUPANCY_SCENARIOS = {"conservador": 0.25, "base": 0.35, "otimista": 0.45}


def seasonality_factor(observed_counts: dict):
    """fator = média anual do índice / média dos meses observados (ponderada por nº obs)."""
    idx = np.array([MONTHLY_INDEX[m] for m in range(1, 13)])
    annual_mean = idx.mean()
    obs_mean = np.average(
        [MONTHLY_INDEX[m] for m in observed_counts.keys()],
        weights=[observed_counts[m] for m in observed_counts.keys()],
    )
    return annual_mean / obs_mean, annual_mean, obs_mean


def main():
    price = load_price()
    mesh = load_mesh()[["listing_id", "suburb", "latitude", "longitude"]]
    details = load_details()
    hosts = load_hosts()

    # hosts dedup pelo snapshot mais recente
    hosts_d = hosts.sort_values("host_snapshot_date").drop_duplicates("owner_id", keep="last")

    # ---- preço por listing (media noite, meses observados) ----
    price_ok = price.dropna(subset=["price"])[price["price"] > 0]
    listings = (mesh.merge(details, on="listing_id", how="inner"))
    listings = listings.merge(hosts_d[["owner_id", "years_host", "months_host", "is_superhost"]],
                              on="owner_id", how="left")

    obs_counts = price_ok.groupby(price_ok["date"].dt.month)["price"].size().to_dict()
    print("Observacoes de preco por mes:", obs_counts)
    factor, annual_mean, obs_mean = seasonality_factor(obs_counts)
    print(f"Indice: media anual={annual_mean:.3f}  media observada(pond)={obs_mean:.3f}  "
          f"fator sazonal={factor:.3f}")
    print(f">>> Preco anual estimado = preco medio observado x {factor:.3f}")

    # ---- agrega por listing ----
    lp = price_ok.groupby("listing_id").agg(
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        n_obs=("price", "size"),
    ).reset_index()

    # ---- perfil por listing ----
    profile = listings.merge(lp, on="listing_id", how="inner")
    profile["listing_type"] = profile["listing_type"].replace(
        {"apartamento": "apartamento", "casa": "casa", "hotel": "hotel", "outros": "outros"}
    )
    profile["beds_group"] = pd.cut(
        profile["number_of_bedrooms"],
        bins=[-1, 0.5, 1.5, 2.5, 3.5, 100],
        labels=["studio", "1 quarto", "2 quartos", "3 quartos", "4+ quartos"],
    )
    # tipo: "compacto" (studio/1q) vs "familia" (3+)
    profile["tipo_compacto"] = profile["beds_group"].isin(["studio", "1 quarto"])
    profile["avg_annual_price"] = profile["avg_price"] * factor

    # ---- índice de demanda corrigido ----
    yrs = profile["years_host"].fillna(0).clip(lower=0.1)
    profile["reviews_per_year"] = profile["number_of_reviews"] / yrs

    # ===================================================== 1. preço por perfil
    print("\n== PREÇO MÉDIO/NOITE OBSERVADO por bairro x tipologia x quartos ==")
    tab = profile.groupby(["suburb", "listing_type", "beds_group"], observed=True).agg(
        n=("listing_id", "size"),
        preco_noite=("avg_price", "mean"),
        preco_anual_proj=("avg_annual_price", "mean"),
    ).reset_index()
    tab = tab[tab["n"] >= 5].sort_values(["suburb", "preco_anual_proj"], ascending=[True, False])

    # salva
    tab.to_csv(os.path.join(OUT, "price_by_profile.csv"), index=False)
    print(tab.round(0).to_string(index=False))

    # ===================================================== 2. demanda mercado
    print("\n== DEMANDA E COMPETIÇÃO por bairro (lista de Airbnb) ==")
    dem = profile.groupby("suburb").agg(
        n_listings=("listing_id", "size"),
        n_zero_rev=("number_of_reviews", lambda s: (s == 0).sum()),
        med_reviews=("number_of_reviews", "median"),
        reviews_por_ano=("reviews_per_year", "median"),
        share_apt=("listing_type", lambda s: (s == "apartamento").mean()),
        preco_anual_proj=("avg_annual_price", "mean"),
    ).reset_index()
    dem["share_zero_reviews"] = dem["n_zero_rev"] / dem["n_listings"]
    dem = dem.sort_values("n_listings", ascending=False)
    dem.to_csv(os.path.join(OUT, "demand_market.csv"), index=False)
    print(dem.round(2).to_string(index=False))

    # ===================================================== 3. receita anual
    print("\n== RECEITA ANUAL PROJETADA (noite) por perfil e cenário de ocupação ==")
    rows = []
    for _, r in tab.iterrows():
        for sc, occ in OCCUPANCY_SCENARIOS.items():
            gross = r["preco_anual_proj"] * 365 * occ
            rows.append({
                "suburb": r["suburb"], "listing_type": r["listing_type"],
                "beds_group": r["beds_group"], "n": r["n"],
                "cenario": sc, "ocupacao": occ,
                "preco_noite_anual": r["preco_anual_proj"],
                "receita_anual_bruta": gross,
            })
    scenarios = pd.DataFrame(rows)
    scenarios.to_csv(os.path.join(OUT, "scenarios.csv"), index=False)
    # pivô: receita base por perfil
    pivot = scenarios[scenarios["cenario"] == "base"].pivot_table(
        index=["suburb", "beds_group"], columns="listing_type",
        values="receita_anual_bruta", aggfunc="first").round(0)
    print("\n-- Receita anual base (35% ocupação) por bairro x quartos (R$) --")
    print(pivot.to_string())

    print(f"\nScript 02 concluído. Arquivos em output/revenue/")
    print(f"Fator sazonal aplicado: x{factor:.3f} (preço médio observado -> projetado anual)")


if __name__ == "__main__":
    main()