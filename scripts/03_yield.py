"""03_yield.py — Lado da compra (VivaReal) x receita Airbnb -> yield líquido por perfil.

Combina:
  - custo de aquisição: preço mediano de venda por (bairro x tipologia x nº quartos), R$/m²;
  - custo fixo: condomínio mensal + IPTU anual;
  - receita líquida anual: receita bruta (cenário ocupação) - condomíniox12 - IPTU - taxa gestão 15%.
  - yield = receita líquida anual / preço de compra.

Gera: output/yield/yield_profiles.csv (+ por cenário de ocupação)
Execução: python scripts/03_yield.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from common import load_vivareal

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "yield")
os.makedirs(OUT, exist_ok=True)

GESTAO_FEE = 0.15          # taxa Seazone sobre receita bruta
IPTU_ASSAY = 0.010         # IPTU anual estimado ~1% do valor de venda (quando ausente)
SCEN_OCUP = {"conservador": 0.25, "base": 0.35, "otimista": 0.45}


def strip_index(s):
    return s.astype(str).str.strip()


def main():
    vr = load_vivareal()

    # filtros de sanidade
    q = vr[(vr["sale_price"] > 30000) & (vr["sale_price"] < 20000000)].copy()
    q["beds_group"] = pd.cut(
        q["bedrooms"], bins=[-1, 0.5, 1.5, 2.5, 3.5, 100],
        labels=["studio", "1 quarto", "2 quartos", "3 quartos", "4+ quartos"],
    )
    q["rspm2"] = q["sale_price"] / q["usable_area"].replace(0, np.nan)

    # ---- perfis relevantes do Airbnb (trazemos de volta para cruzar) ----
    # Perfis com dados suficientes no lado da oferta (de 02_revenue)
    profiles = pd.read_csv(os.path.join(os.path.dirname(OUT), "revenue", "price_by_profile.csv"))
    # receita base por perfil
    sc = pd.read_csv(os.path.join(os.path.dirname(OUT), "revenue", "scenarios.csv"))

    print("== MERCADO DE COMPRA (VivaReal): mediana por bairro x tipo x quartos ==")
    agg = q.groupby(["suburb", "beds_group"], observed=True).agg(
        n=("listing_id", "size"),
        med_preco=("sale_price", "median"),
        med_m2=("rspm2", "median"),
        med_area=("usable_area", "median"),
        med_condo=("monthly_condo_fee", "median"),
        med_iptu=("yearly_iptu", "median"),
    ).reset_index()
    agg = agg[agg["n"] >= 5].sort_values(["suburb", "beds_group"])
    print(agg.round(0).to_string(index=False))
    agg.to_csv(os.path.join(OUT, "compra_perfil.csv"), index=False)

    # ---- cruza receita com custo de compra -> construímos o "produto" ----
    # receita: agrega cenário base por (suburb, beds_group) para apartamento
    rev_base = sc[sc["cenario"] == "base"].groupby(["suburb", "beds_group"], observed=True).agg(
        receita_bruta=("receita_anual_bruta", "first"),
        preco_noite=("preco_noite_anual", "first"),
        n_oferta=("n", "first"),
    ).reset_index()

    # custo de compra por perfil (apartamento)
    compra = q[q["listing_type"] == "apartamento"].groupby(
        ["suburb", "beds_group"], observed=True).agg(
        med_preco=("sale_price", "median"),
        med_condo=("monthly_condo_fee", "median"),
        med_iptu=("yearly_iptu", "median"),
        med_area=("usable_area", "median"),
        n_compra=("listing_id", "size"),
    ).reset_index()

    m = rev_base.merge(compra, on=["suburb", "beds_group"], how="inner")

    rows = []
    for _, r in m.iterrows():
        preco = r["med_preco"]
        condo_anual = (r["med_condo"] if pd.notna(r["med_condo"]) else 0) * 12
        iptu = r["med_iptu"] if pd.notna(r["med_iptu"]) else preco * IPTU_ASSAY
        fixo = condo_anual + iptu
        for sc_name, occ in SCEN_OCUP.items():
            bruta = r["receita_bruta"] * (occ / 0.35)  # escala pela ocupação
            liquida = bruta * (1 - GESTAO_FEE) - fixo
            yield_bruto = bruta / preco
            yield_liquido = liquida / preco
            rows.append({
                "suburb": r["suburb"], "beds_group": r["beds_group"],
                "preco_compra": preco, "area_m2": r["med_area"],
                "condo_anual": condo_anual, "iptu_anual": iptu,
                "custo_fixo_anual": fixo,
                "cenario": sc_name, "ocupacao": occ,
                "receita_bruta": bruta, "receita_liquida": liquida,
                "yield_bruto": yield_bruto, "yield_liquido": yield_liquido,
                "n_oferta": r["n_oferta"], "n_compra": r["n_compra"],
            })
    yd = pd.DataFrame(rows)
    yd.to_csv(os.path.join(OUT, "yield_profiles.csv"), index=False)

    print("\n== YIELD LÍQUIDO por perfil (cenário base, 35% ocupação) ==")
    base = yd[yd["cenario"] == "base"].sort_values("yield_liquido", ascending=False)
    print(base[["suburb", "beds_group", "preco_compra", "receita_bruta",
                "receita_liquida", "custo_fixo_anual", "yield_bruto", "yield_liquido"]]
          .round(0).assign(yield_bruto=lambda d: d["yield_bruto"] * 100,
                           yield_liquido=lambda d: d["yield_liquido"] * 100)
          .to_string(index=False))

    print("\n-- Resumo: qual perfil lidera o yield? (base) --")
    top = base.head(8)[["suburb", "beds_group", "yield_liquido"]].copy()
    top["yield_liquido_pct"] = (top["yield_liquido"] * 100).round(2)
    print(top.to_string(index=False))

    print(f"\nScript 03 concluído. Arquivo: output/yield/yield_profiles.csv")


if __name__ == "__main__":
    main()