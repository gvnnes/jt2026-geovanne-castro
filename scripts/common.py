"""Módulo compartilhado: carregamento e normalização das bases de Itapema.

Uso:
    import sys; sys.path.insert(0, 'scripts')
    from common import load_all
    details, mesh, hosts, price, vr = load_all()
"""
import pandas as pd
import numpy as np
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------------------
# Bairros: normalização (case-insensitive, sem acento, com variantes)
# ---------------------------------------------------------------------------
SUBURB_ALIASES = {
    "meia praia": "Meia Praia",
    "meia praia - frente mar": "Meia Praia",
    "meia praia frente mar": "Meia Praia",
    "centro": "Centro",
    "morretes": "Morretes",
    "andorinha": "Andorinha",
    "castelo branco": "Castelo Branco",
    "tabuleiro dos oliveiras": "Tabuleiro dos Oliveiras",
    "tabuleiro": "Tabuleiro dos Oliveiras",
    "taboleiro": "Tabuleiro dos Oliveiras",
    "canto da praia": "Canto da Praia",
    "jardim praia mar": "Jardim Praia Mar",
    "jardim praiamar": "Jardim Praia Mar",
    "casa branca": "Casa Branca",
    "alto são bento": "Alto Sao Bento",
    "alto sao bento": "Alto Sao Bento",
    "ilhota": "Ilhota",
    "varzea": "Varzea",
    "varge": "Varzea",
    "sertão do trombudo": "Sertao do Trombudo",
    "sertao do trombudo": "Sertao do Trombudo",
    "sertaozinho": "Sertaozinho",
    "leopoldo zarling": "Leopoldo Zarling",
    "areal": "Areal",
    "lameiro": "Lameiro",
    "ocean tower": "Centro",
    "estreito": "Estreito",
    "itapema": "Outros Itapema",
    "none": "na",
    "": "na",
    "na": "na",
}


def norm_suburb(s):
    if s is None:
        return "na"
    key = " ".join(str(s).strip().lower().split())
    key = key.replace("ã", "a").replace("õ", "o").replace("é", "e").replace("ê", "e")
    return SUBURB_ALIASES.get(key, str(s).strip())


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def _n(s):
    """Converte string numérica ou retorna NaN."""
    if s is None or (isinstance(s, str) and s.strip() in ("", "<NA>", "NA", "None", "null")):
        return np.nan
    try:
        return float(s)
    except (ValueError, TypeError):
        return np.nan


def _num_cols(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map(_n)
    return df


def load_details():
    """Details_Itapema.csv — anúncios Airbnb. Mantém cols-chave como strings."""
    df = pd.read_csv(os.path.join(DATA, "Details_Itapema.csv"), dtype=str, low_memory=False)
    df.rename(columns={"airbnb_listing_id": "listing_id"}, inplace=True)
    df["listing_id"] = df["listing_id"].str.strip()
    df["number_of_bedrooms"] = df["number_of_bedrooms"].map(_n)
    df["number_of_reviews"] = df["number_of_reviews"].map(_n)
    df["star_rating"] = df["star_rating"].map(_n)
    df["cleaning_fee"] = df["cleaning_fee"].map(_n)
    df["number_of_guests"] = df["number_of_guests"].map(_n)
    df["number_of_bathrooms"] = df["number_of_bathrooms"].map(_n)
    return df


def load_mesh():
    df = pd.read_csv(os.path.join(DATA, "Mesh_Ids_Data_Itapema.csv"), dtype=str)
    df.rename(columns={"airbnb_listing_id": "listing_id"}, inplace=True)
    df["listing_id"] = df["listing_id"].str.strip()
    df["latitude"] = df["latitude"].map(_n)
    df["longitude"] = df["longitude"].map(_n)
    df["suburb"] = df["suburb"].fillna("").map(norm_suburb)
    return df


def load_hosts():
    df = pd.read_csv(os.path.join(DATA, "Hosts_ids_Itapema.csv"), dtype=str)
    df["owner_id"] = df["owner_id"].astype(str).str.strip()
    df["years_host"] = df["years_host"].map(_n)
    df["months_host"] = df["months_host"].map(_n)
    df["number_of_reviews_host"] = df["number_of_reviews_host"].map(_n)
    df["response_rate_shown"] = df["response_rate_shown"].map(_n)
    df["star_rating_host"] = df["star_rating_host"].map(_n)
    df["is_superhost"] = df["is_superhost"].map(
        lambda x: True if isinstance(x, str) and x.strip().lower() == "true" else False
    )
    return df


def load_price():
    """Price_AV_Itapema.csv — preço por listing/date. Diversas capturas por data."""
    df = pd.read_csv(os.path.join(DATA, "Price_AV_Itapema.csv"), dtype=str)
    df.rename(columns={"airbnb_listing_id": "listing_id"}, inplace=True)
    df["listing_id"] = df["listing_id"].str.strip()
    df["price"] = df["price"].map(_n)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_vivareal():
    df = pd.read_csv(os.path.join(DATA, "VivaReal_Itapema.csv"), dtype=str)
    df["sale_price"] = df["sale_price"].map(_n)
    df["rental_price"] = df["rental_price"].map(_n)
    df["usable_area"] = df["usable_area"].map(_n)
    df["bedrooms"] = df["bedrooms"].map(_n)
    df["bathrooms"] = df["bathrooms"].map(_n)
    df["parking_spaces"] = df["parking_spaces"].map(_n)
    df["yearly_iptu"] = df["yearly_iptu"].map(_n)
    df["monthly_condo_fee"] = df["monthly_condo_fee"].map(_n)
    df["suburb"] = df["suburb"].fillna("").map(norm_suburb)
    return df


def load_all():
    return {
        "details": load_details(),
        "mesh": load_mesh(),
        "hosts": load_hosts(),
        "price": load_price(),
        "vivareal": load_vivareal(),
    }