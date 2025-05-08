import pandas as pd
import logging

def calculer_kpis_ventes(df):
    logging.info("📊 Calcul des KPI de ventes...")

    # ✅ Nettoyage des colonnes
    df.columns = [col.strip() for col in df.columns]

    # ✅ Vérification des colonnes nécessaires
    required_cols = ["Date vente", "Culture", "Variété", "Quantité vendue", "Prix au kg"]
    for col in required_cols:
        if col not in df.columns:
            logging.warning(f"Colonne manquante : {col}")
            return pd.DataFrame()

    # ✅ Traitement des types
    df["Date vente"] = pd.to_datetime(df["Date vente"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["Date vente"])
    df["Quantité vendue"] = pd.to_numeric(df["Quantité vendue"], errors="coerce")
    df["Prix au kg"] = pd.to_numeric(df["Prix au kg"], errors="coerce")
    df["Culture"] = df["Culture"].astype(str).str.strip()
    df["Variété"] = df["Variété"].astype(str).str.strip()

    # ✅ Périodes temporelles
    df["Mois"] = df["Date vente"].dt.to_period("M").astype(str)
    df["Année"] = df["Date vente"].dt.year.astype(str)

    kpi_frames = []

    # ✅ KPI : Quantité vendue par Mois + Culture + Variété
    kpi_quantite = (
        df.groupby(["Mois", "Culture", "Variété"])["Quantité vendue"]
        .sum()
        .reset_index()
        .assign(KPI="par_mois", Type="vente")
    )
    kpi_quantite["Année"] = kpi_quantite["Mois"].str.slice(0, 4)
    kpi_frames.append(kpi_quantite)

    # ✅ KPI : Prix moyen par Mois + Culture + Variété
    kpi_prix = (
        df.dropna(subset=["Prix au kg"])
        .groupby(["Mois", "Culture", "Variété"])["Prix au kg"]
        .mean()
        .reset_index()
        .assign(KPI="prix_moyen_par_mois", Type="vente")
    )
    kpi_prix["Année"] = kpi_prix["Mois"].str.slice(0, 4)
    kpi_frames.append(kpi_prix)

    # ✅ Fusion des KPI
    final_df = pd.concat(kpi_frames, ignore_index=True)

    # ✅ Colonnes standardisées
    columns_order = ["Type", "KPI", "Culture", "Variété", "Quantité vendue", "Prix au kg", "Mois", "Année"]
    for col in columns_order:
        if col not in final_df.columns:
            final_df[col] = None

    logging.info("✅ KPI de ventes calculés.")
    return final_df[columns_order]
