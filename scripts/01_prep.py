"""01_prep.py — Carrega, normaliza, cruza as bases e guarda o dataset consolidado.

Gera:
  output/clean/ {
    listings_with_price.csv  (details + mesh, só quem tem preço)
    price_per_listing.csv    (preço médio/noite por listing + datas observadas)
    vivareal_clean.csv
  }
Execução: python scripts/01_prep.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from common import load_all

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "clean")
os.makedirs(OUT, exist_ok=True)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)


def main():
    d = load_all()
    details, mesh, hosts, price, vr = d["details"], d["mesh"], d["hosts"], d["price"], d["vivareal"]

    print("=" * 90)
    print("LEITURA & COUNT")
    print("=" * 90)
    for name, df in d.items():
        print(f"  {name:12s} linhas={len(df):>7}  colunas={df.shape[1]}")

    # ---- Preço: limpeza e agregação por listing ----
    kept = price.dropna(subset=["price"]).copy()
    outliers = kept[kept["price"] <= 0]
    kept = kept[kept["price"] > 0]
    print(f"\nPrice: linhas={len(price)}  com preço válido={len(kept)}  descartadas={len(price)-len(kept)}")
    print(f"Preço por noite: p5=${kept['price'].quantile(.05):.0f}  mediana=${kept['price'].median():.0f} "
          f"p95=${kept['price'].quantile(.95):.0f}  max=${kept['price'].max():.0f}")

    grp = kept.groupby("listing_id").agg(
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        min_date=("date", "min"),
        max_date=("date", "max"),
        n_observations=("price", "size"),
        n_unique_dates=("date", "nunique"),
        season_high=("price", lambda s: s.mean()),  # placeholder; calculamos depois
    ).reset_index()

    print(f"\nListings distintos com preço: {grp['listing_id'].nunique()}")
    print("Dados de preço por listing:")
    print(grp.describe().round(1))

    # ---- Junta details + mesh para todos os listings ----
    dm = details.merge(mesh[["listing_id", "latitude", "longitude", "suburb"]],
                       on="listing_id", how="left", validate="1:1")
    print(f"\nDetails+mesh: {len(details)} details; com bairro={dm['suburb'].notna().sum()} "
          f"({dm['suburb'].notna().mean()*100:.1f}%)")

    # ---- Viés: perfil dos que têm preço vs todos ----
    with_price = dm.merge(grp[["listing_id"]], on="listing_id", how="inner")
    all_ = dm

    def profile(df):
        return pd.Series({
            "n": len(df),
            "apt": (df["listing_type"] == "apartamento").mean(),
            "casa": (df["listing_type"] == "casa").mean(),
            "bedrooms_med": df["number_of_bedrooms"].median(),
            "bedrooms1": (df["number_of_bedrooms"] == 1).mean(),
            "bedrooms2": (df["number_of_bedrooms"] == 2).mean(),
            "bedrooms3": (df["number_of_bedrooms"] == 3).mean(),
            "clean_fee_present": df["cleaning_fee"].notna().mean(),
            "guests_med": df["number_of_guests"].median(),
        })

    print("\n-- Viés da amostra (com preço vs universo) --")
    print(pd.concat({"com_preco": profile(with_price), "universo": profile(all_)}, axis=1).T.round(2))

    # Bairros: universo vs com preço
    sub_all = all_["suburb"].value_counts(dropna=False)
    sub_wp = with_price["suburb"].value_counts(dropna=False)
    print("\n-- Bairros: universo vs com preço (share) --")
    tab = pd.DataFrame({"universo": sub_all, "com_preco": sub_wp}).fillna(0)
    tab["share_universo"] = (tab["universo"] / tab["universo"].sum() * 100).round(1)
    tab["share_com_preco"] = (tab["com_preco"] / tab["com_preco"].sum() * 100).round(1)
    print(tab.sort_values("universo", ascending=False))

    # ---- Merge final: listings com preço enriquecido com hosts ----
    # hosts pode ter várias linhas por owner (snapshots): fica com a mais recente
    n_owners_all = hosts["owner_id"].nunique()
    hosts_dedup = hosts.sort_values("host_snapshot_date").drop_duplicates(
        "owner_id", keep="last")
    print(f"\nHosts: linhas={len(hosts)} owner distintos={n_owners_all} "
          f"(dedup={len(hosts_dedup)})")

    full = with_price.merge(grp[["listing_id", "avg_price", "median_price", "min_date", "max_date",
                                 "n_observations", "n_unique_dates"]],
                            on="listing_id", how="left")
    full = full.merge(hosts_dedup[["owner_id", "is_superhost", "years_host", "months_host",
                                   "number_of_reviews_host", "star_rating_host"]],
                      left_on="owner_id", right_on="owner_id", how="left")

    # Índice de demanda: reviews anualizados (reviews / anos de existência)
    ref_date = pd.Timestamp("2025-04-20")
    aquis = pd.to_datetime(full["aquisition_date"], errors="coerce")
    full["years_listed"] = ((ref_date - aquis).dt.days / 365.25).clip(lower=0.1)
    full["reviews_per_year"] = full["number_of_reviews"] / full["years_listed"]

    full.to_csv(os.path.join(OUT, "listings_with_price.csv"), index=False)
    grp.to_csv(os.path.join(OUT, "price_per_listing.csv"), index=False)
    vr.to_csv(os.path.join(OUT, "vivareal_clean.csv"), index=False)

    print("\nSalvo em output/clean/"
          "{listings_with_price.csv, price_per_listing.csv, vivareal_clean.csv}")
    print(f"\nListings com preço + bairro: {full['suburb'].notna().sum()}")
    print("Amostras do índice de demanda (reviews/ano): p25="
          f"{full['reviews_per_year'].quantile(.25):.1f} mediana="
          f"{full['reviews_per_year'].median():.1f} p75="
          f"{full['reviews_per_year'].quantile(.75):.1f}")


if __name__ == "__main__":
    main()