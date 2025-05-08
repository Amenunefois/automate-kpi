import streamlit as st
import pandas as pd
import altair as alt
from filters import filtres_recoltes, filtres_ventes, filtres_evolution_prix
import streamlit as st
import subprocess
import time

st.set_page_config(page_title="Dashboard Agricole", layout="wide")

@st.cache_resource
def update_data():
    msg = st.empty()  # conteneur temporaire
    msg.info("🔄 Mise à jour des données (unique par session)...")

    result = subprocess.run(["python", "run_all.py"], capture_output=True, text=True)

    msg.empty()  # efface le message

    return result

# 📦 Lancer une seule fois
result = update_data()

if result.returncode == 0:
    message = st.empty()
    
else:
    st.error("❌ Erreur pendant la mise à jour des données.")
    st.text(result.stderr)


# ✅ Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("kpi_consolidated.csv")

    # 🧼 Nettoyage NaN
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # 🔧 Forçage des colonnes string
    force_str_cols = ["Année", "Parcelle", "Mois", "Trimestre", "Culture", "Variété"]
    for col in force_str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    return df


df = load_data()

# 🎛️ Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Vue", ["🌾 Récoltes par culture", "💰 Ventes par culture","📈 Évolution du prix mensuel"])

# === 🌾 RÉCOLTES ===
if page == "🌾 Récoltes par culture":
    recolte_df = df[df["Type"] == "recolte"]
    recolte_df = filtres_recoltes(recolte_df)

    if not recolte_df.empty:
        st.subheader("🌾 Quantité récoltée par culture")
        chart = alt.Chart(recolte_df).mark_bar().configure_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            fillOpacity=0.85,
            strokeWidth=0.5
        ).encode(
            x=alt.X("Culture:N", sort="-x"),
            y=alt.Y("Quantité récoltée:Q", title="Quantité récoltée (kg)"),
            tooltip=["Culture", "Variété", "Quantité récoltée"],
            color="Culture:N"
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(recolte_df[["Culture", "Variété", "Quantité récoltée", "Mois", "Année"]])
    else:
        st.warning("Aucune donnée de récolte.")

# === 💰 VENTES ===
elif page == "💰 Ventes par culture":
    vente_df = df[df["Type"] == "vente"]
    vente_df = filtres_ventes(vente_df)

    if not vente_df.empty:
        st.subheader("💰 Quantité vendue par culture")
        chart = alt.Chart(vente_df).mark_bar().configure_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            fillOpacity=0.85,
            strokeWidth=0.5
        ).encode(
            x=alt.X("Culture:N", sort="-x"),
            y=alt.Y("Quantité vendue:Q", title="Quantité vendue (kg)"),
            tooltip=["Culture", "Variété", "Quantité vendue"],
            color="Culture:N",
            shape="Variété:N"
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(vente_df[["Culture", "Variété", "Quantité vendue", "Mois", "Année"]])
    else:
        st.warning("Aucune donnée de vente.")

elif page == "📈 Évolution du prix mensuel":
    st.subheader("📈 Évolution du prix moyen par culture (€/kg)")

    prix_df = df[(df["Type"] == "vente") & (df["KPI"] == "prix_moyen_par_mois")].copy()
    prix_df = filtres_evolution_prix(prix_df)

    if prix_df.empty:
        st.warning("Aucune donnée de prix disponible.")
    else:
        prix_df["Mois"] = prix_df["Mois"].astype(str).str.strip()
        prix_df["Année"] = prix_df["Mois"].str[:4]
        prix_df["Prix au kg"] = pd.to_numeric(prix_df.get("Prix au kg", 0), errors="coerce").fillna(0)


        filtered = prix_df.copy()
        if not filtered.empty:
            chart = alt.Chart(filtered).mark_line(point=True).encode(
                x="Mois:N",
                y=alt.Y("Prix au kg:Q", title="Prix moyen (€/kg)"),
                color="Culture:N",
                tooltip=["Mois", "Culture", "Prix au kg"]
            ).properties(height=400)

            st.altair_chart(chart, use_container_width=True)

            st.markdown("### 📋 Données")
            st.dataframe(filtered[["Mois", "Culture", "Prix au kg"]], use_container_width=True)
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")

