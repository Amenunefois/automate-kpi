import os
import sys
import logging
import pandas as pd
import gspread
from dotenv import dotenv_values
from oauth2client.service_account import ServiceAccountCredentials

# 📦 Résolution robuste du répertoire racine (même avec PyInstaller)
def resolve_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # mode PyInstaller
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

BASE_PATH = resolve_base_path()

# 🔐 Chargement sécurisé du fichier .env
env_path = os.path.join(BASE_PATH, '.env')
env_vars = dotenv_values(env_path)

CREDENTIALS_PATH = os.path.join(BASE_PATH, env_vars.get("GOOGLE_CREDS", "credentials/credentials.json"))
SHEET_NAME = env_vars.get("SHEET_NAME", "")
SHEET_TAB = env_vars.get("SHEET_TAB", "Feuille 1")

# ✅ Vérification de sécurité
if not SHEET_NAME:
    raise ValueError("SHEET_NAME est manquant dans le fichier .env")
if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(f"Fichier credentials introuvable : {CREDENTIALS_PATH}")

# 📂 Configuration des logs
log_dir = os.path.join(BASE_PATH, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'fetch.log')

logging.basicConfig(
    filename=log_path,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logging.getLogger().addHandler(console)

def fetch_data_from_sheet():
    try:
        logging.info("📡 Connexion à Google Sheets...")
        print(f"🔍 SHEET_NAME = {SHEET_NAME}")
        print(f"🔍 SHEET_TAB = {SHEET_TAB}")

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
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

if __name__ == "__main__":
    fetch_data_from_sheet()
