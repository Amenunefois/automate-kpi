import subprocess

def run_command(command, desc, cwd=None):
    print(f"\n🚀 {desc}...")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode == 0:
        print(f"✅ {desc} terminé avec succès.")
    else:
        print(f"❌ Erreur pendant : {desc}")
        exit(1)

# 1. Récupération des données Google Sheets
run_command("python src/fetch_sheet.py", "Récupération des données Google Sheets")

# 2. Calcul des KPI
run_command("python -m kpi.run_kpi", "Calcul des KPI à partir de data_export.csv", cwd="src")

# 3. Pousser vers BDD Notion
# run_command("python src/push_to_notion.py", "Synchronisation des KPI dans Notion")
