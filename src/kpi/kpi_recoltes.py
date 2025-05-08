import pandas as pd
import logging

def calculer_kpis_recoltes(df):
    logging.info("🌾 Calcul des KPI de récoltes...")

    # Nettoyage des noms de colonnes
    df.columns = [col.strip() for col in df.columns]

    # Vérification des colonnes nécessaires
    required_cols = ["Date vente","Variété", "Quantité produite", "Culture"]
    for col in required_cols:
        if col not in df.columns:
            logging.warning(f"Colonne manquante : {col}")
            return pd.DataFrame()

    # Conversion des types
    df["Date vente"] = pd.to_datetime(df["Date vente"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["Date vente"])
    df["Quantité produite"] = pd.to_numeric(df["Quantité produite"], errors="coerce")
    df["Culture"] = df["Culture"].astype(str).str.strip()

    # Création des périodes
    df["Mois"] = df["Date vente"].dt.to_period("M").astype(str)
    df["Année"] = df["Date vente"].dt.year.astype(str)
    df["Variété"] = df["Variété"].astype(str).str.strip()  # nettoyage variété


    # KPI : Quantité récoltée par Mois + Culture
    kpi = (
        df.groupby(["Mois", "Culture","Variété"])["Quantité produite"]
        .sum()
        .reset_index()
        .assign(KPI="par_mois", Type="recolte")
    )

    # Ajout de l’année extraite du mois
    kpi["Année"] = kpi["Mois"].str[:4]

    # Harmonisation des colonnes
    kpi = kpi.rename(columns={"Quantité produite": "Quantité récoltée"})
    columns_order = ["Type", "KPI", "Culture", "Variété", "Quantité récoltée", "Mois", "Année"]
    for col in columns_order:
        if col not in kpi.columns:
            kpi[col] = None

    logging.info("✅ KPI de récoltes calculé.")
    return kpi[columns_order]
