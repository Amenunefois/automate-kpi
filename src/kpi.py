import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard Agricole", layout="wide")

# ✅ Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("kpi_consolidated.csv")
    df.fillna("", inplace=True)
    df["Année"] = df["Année"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    df["Culture"] = df["Culture"].astype(str).str.strip()
    return df

df = load_data()

# 🎛️ Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Vue", ["🌾 Récoltes par culture", "💰 Ventes par culture"])

# 🎛️ Filtres
annees = sorted(df["Année"].dropna().unique())
cultures = sorted(df["Culture"].dropna().unique())

selected_annee = st.sidebar.selectbox("📅 Année", ["Toutes"] + annees)
selected_culture = st.sidebar.selectbox("🌿 Culture", ["Toutes"] + cultures)

# 📦 Filtrage global
filtered_df = df.copy()
if selected_annee != "Toutes":
    filtered_df = filtered_df[filtered_df["Année"] == selected_annee]
if selected_culture != "Toutes":
    filtered_df = filtered_df[filtered_df["Culture"] == selected_culture]

# === 🌾 RÉCOLTES ===
if page == "🌾 Récoltes par culture":
    recolte_df = filtered_df[filtered_df["Type"] == "recolte"]

    if not recolte_df.empty:
        st.subheader("🌾 Quantité récoltée par culture")
        chart = alt.Chart(recolte_df).mark_bar().encode(
            x=alt.X("Quantité récoltée:Q", title="Quantité récoltée (kg)"),
            y=alt.Y("Culture:N", sort="-x"),
            tooltip=["Culture", "Quantité récoltée"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(recolte_df[["Culture", "Quantité récoltée", "Année"]])
    else:
        st.warning("Aucune donnée de récolte.")

# === 💰 VENTES ===
elif page == "💰 Ventes par culture":
    vente_df = filtered_df[filtered_df["Type"] == "vente"]

    if not vente_df.empty:
        st.subheader("💰 Quantité vendue par culture")
        chart = alt.Chart(vente_df).mark_bar().encode(
            x=alt.X("Quantité vendue:Q", title="Quantité vendue (kg)"),
            y=alt.Y("Culture:N", sort="-x"),
            tooltip=["Culture", "Quantité vendue"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(vente_df[["Culture", "Quantité vendue", "Année"]])
    else:
        st.warning("Aucune donnée de vente.")
