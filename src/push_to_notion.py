import os
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Connexion à l'API Notion
notion = Client(auth=NOTION_TOKEN)

# 🔁 Archiver toutes les anciennes lignes
def clear_database(database_id):
    print("🧹 Nettoyage de la base Notion...")
    pages = notion.databases.query(database_id=database_id)["results"]
    for page in pages:
        notion.pages.update(page_id=page["id"], archived=True)
        print(f"🗑 Page {page['id']} archivée.")
    print(f"✅ {len(pages)} lignes archivées.")

clear_database(NOTION_DATABASE_ID)

# 📥 Charger les données à envoyer
df = pd.read_csv("kpi_consolidated.csv")

# Remplir proprement les valeurs manquantes
for col in df.columns:
    if df[col].dtype == "float64" or df[col].dtype == "int64":
        df[col] = df[col].fillna(0)
    else:
        df[col] = df[col].fillna("")

# 🧱 Mapper une ligne vers une page Notion
def to_notion_page(row):
    props = {
        "Type": {"select": {"name": row["Type"]}},
        "KPI": {"select": {"name": row["KPI"]}},
        "Culture": {"rich_text": [{"text": {"content": row["Culture"]}}]} if row["Culture"] else {},
        "Variété": {"rich_text": [{"text": {"content": row["Variété"]}}]} if row["Variété"] else {},
        "Parcelle": {"number": float(row["Parcelle"])} if row["Parcelle"] != "" else {},
        "Quantité récoltée": {"number": int(row["Quantité récoltée"])} if row["Quantité récoltée"] != "" else {},
        "Mois": {"rich_text": [{"text": {"content": row["Mois"]}}]} if row["Mois"] else {},
        "Trimestre": {"rich_text": [{"text": {"content": row["Trimestre"]}}]} if row["Trimestre"] else {},
        "Année": {"number": int(row["Année"])} if row["Année"] != "" else {},
    }
    props = {k: v for k, v in props.items() if v}
    return {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": props
    }

# 🚀 Pousser chaque ligne
print("🚀 Envoi des lignes dans Notion...")
for i, row in df.iterrows():
    try:
        notion.pages.create(**to_notion_page(row))
        print(f"✅ Ligne {i+1} envoyée.")
    except Exception as e:
        print(f"❌ Erreur ligne {i+1} : {e}")