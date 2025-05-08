import pandas as pd
import logging
import os
from .kpi_recoltes import calculer_kpis_recoltes
from .kpi_ventes import calculer_kpis_ventes

logging.basicConfig(level=logging.INFO)

def run_all_kpis():
    source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data_export.csv"))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../kpi_consolidated.csv"))

    try:
        df = pd.read_csv(source_path)
        logging.info(f"✅ Fichier source chargé avec {len(df)} lignes")
    except Exception as e:
        logging.exception("Erreur de lecture du fichier source")
        return

    try:
        df_recoltes = calculer_kpis_recoltes(df)
        df_ventes = calculer_kpis_ventes(df)
        all_kpis = pd.concat([df_recoltes, df_ventes], ignore_index=True)
        all_kpis.to_csv(output_path, index=False)
        logging.info(f"✅ Données exportées dans : {output_path}")
    except Exception as e:
        logging.exception("Erreur lors du calcul ou de l'export des KPI")

if __name__ == "__main__":
    run_all_kpis()