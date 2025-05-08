# streamlit_app/filters.py
import streamlit as st

def filtres_recoltes(df):
    st.markdown("#### 🎛️ Filtres récoltes")
    col1, col2 = st.columns(2)

    with col1:
        annees = sorted(df["Année"].dropna().unique())
        selected_annee = st.selectbox("📅 Année", ["Toutes"] + annees, key="recolte_annee")
    with col2:
        cultures = sorted(df["Culture"].dropna().unique())
        selected_culture = st.selectbox("🥕 Culture", ["Toutes"] + cultures, key="recolte_culture")

    if selected_annee != "Toutes":
        df = df[df["Année"] == selected_annee]
    if selected_culture != "Toutes":
        df = df[df["Culture"] == selected_culture]

    return df

def filtres_ventes(df):
    st.markdown("#### 🎛️ Filtres ventes")
    col1, col2 = st.columns(2)

    with col1:
        annees = sorted(df["Année"].dropna().unique())
        selected_annee = st.selectbox("📅 Année", ["Toutes"] + annees, key="vente_annee")
    with col2:
        cultures = sorted(df["Culture"].dropna().unique())
        selected_culture = st.selectbox("🍉 Culture", ["Toutes"] + cultures, key="vente_culture")

    if selected_annee != "Toutes":
        df = df[df["Année"] == selected_annee]
    if selected_culture != "Toutes":
        df = df[df["Culture"] == selected_culture]

    return df

def filtres_evolution_prix(prix_df):
    st.markdown("#### 🎛️ Filtres évolution des prix")
    col1, col2 = st.columns(2)

    with col1:
        annees_dispo = sorted(prix_df["Année"].dropna().unique())
        selected_year = st.selectbox("📅 Année", ["Toutes"] + annees_dispo, key="prix_annee")

    with col2:
        cultures_dispo = sorted(prix_df["Culture"].dropna().unique())
        selected_culture = st.selectbox("🥕 Culture", ["Toutes"] + cultures_dispo, key="prix_culture")


    if selected_year != "Toutes":
        prix_df = prix_df[prix_df["Année"] == selected_year]
    if selected_culture != "Toutes":
        prix_df = prix_df[prix_df["Culture"] == selected_culture]
    return prix_df