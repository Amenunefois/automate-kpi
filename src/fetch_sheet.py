import os
import json
import logging
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# === 📁 Configuration cloud ===
CREDENTIALS_JSON = json.loads(st.secrets["GOOGLE_CREDS"])
SHEET_NAME = st.secrets["SHEET_NAME"]
SHEET_TAB = st.secrets.get("SHEET_TAB", "Feuille 1")
BASE_PATH = "/tmp"

# === 📂 Configuration des logs ===
log_dir = os.path.join(BASE_PATH, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'fetch.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_data_from_sheet():
    try:
        logging.info("📡 Connexion à Google Sheets...")
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS_JSON, scope)
        client = gspread.authorize(creds)

        sheet = client.open(SHEET_NAME).worksheet(SHEET_TAB)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        if "Timestamp" in df.columns:
            df.drop(columns=["Timestamp"], inplace=True)

        logging.info(f"{len(df)} lignes chargées.")

        # 🔄 Fusion contextuelle des colonnes de variétés
        culture_col = "Culture"
        variete_cols = [col for col in df.columns if "Variétés" in col or "Variété" in col]
        if variete_cols and culture_col in df.columns:
            def detect_variete(row):
                culture = row[culture_col].strip().lower()
                for col in variete_cols:
                    if culture in col.lower():
                        return row[col]
                return ""
            df["Variété"] = df.apply(detect_variete, axis=1)
            df.drop(columns=variete_cols, inplace=True)
            
        # 🔁 Uniformisation des noms de colonnes
        df = df.rename(columns={
            "Date": "Date vente",
            "Quantité vendue (kg)": "Quantité vendue",
            "Quantité produite (kg)": "Quantité produite",
            "Prix au kg (€)": "Prix au kg"
        })
        # 🧼 Nettoyage final
        df.columns = [col.strip() for col in df.columns]
        df.fillna("", inplace=True)

        # 💾 Export
        output_path = os.path.join(BASE_PATH, 'data_export.csv')
        df.to_csv(output_path, index=False)
        logging.info(f"💾 Données sauvegardées dans {output_path}")

    except Exception as e:
        logging.exception("❌ Erreur lors de la récupération des données.")
        raise e
