import streamlit as st
from analysis.indicators import TrajetAnalyse
from api.fetch_data_tgvmax import fetch_data_with_csv_cache, fetch_unique_stations
import os

# Configurer la page
st.set_page_config(page_title="Ma Ligne TGV Max", page_icon="🚆", layout="wide")

# Interface principale
st.title("Ma Ligne TGV Max 🚆")

# Sélection des trajets

# Charger la liste des gares dynamiquement
st.sidebar.header("🚉 Sélection du trajet")
stations = fetch_unique_stations()
if stations:
    departure = st.sidebar.selectbox("Gare de départ", stations)
    arrival = st.sidebar.selectbox("Gare d'arrivée", stations)
else:
    st.sidebar.error("Impossible de récupérer la liste des gares. Vérifiez votre connexion ou l'API.")

fetch_data = st.sidebar.button("Charger les données")

# Chargement des données
if fetch_data:
    cache_file_path = fetch_data_with_csv_cache(
        départ=departure, arrivée=arrival)

    if cache_file_path and os.path.exists(cache_file_path):
        st.success(f"Données chargées pour {departure} -> {arrival}")
        st.session_state["file_path"] = cache_file_path
    elif os.path.join('dashboard/data/cache', f"{departure.replace(' ', '_')}_to_{arrival.replace(' ', '_')}.csv"):
        cache_file_path=os.path.join('dashboard/data/cache', f"{departure.replace(' ', '_')}_to_{arrival.replace(' ', '_')}.csv")
        st.success(f"Données chargées pour {departure} -> {arrival}")
        st.session_state["file_path"] = cache_file_path

    else:
        st.error("Aucune donnée disponible ou mise à jour pour ce trajet.")

# Affichage des données et graphiques
if "file_path" in st.session_state and os.path.exists(st.session_state["file_path"]):
    # Charger les données et initialiser l’analyse
    file_path = st.session_state["file_path"]
    analyse = TrajetAnalyse(file_path)

    # Section des filtres
    st.sidebar.header("📊 Filtres")
    year = st.sidebar.selectbox("Année", analyse.df_complet["date"].dt.year.unique())
    month = st.sidebar.selectbox("Mois", range(1, 13))  # Mois de 1 à 12
    trajet_type = st.sidebar.radio("Type de trajet", ["OUI", "NON"])

    # Afficher les KPI
    # Afficher les KPI
    st.header(f"🚄 Indicateurs pour {departure} -> {arrival}")
    kpis = analyse.kpi_summary()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trajets", kpis["total_trajets"])
    col2.metric("Disponibles (%)", kpis["taux_dispo"])
    col3.metric("Worth Score", kpis["worth_score"])


    # Afficher le graphique mensuel
    st.header("📈 Évolution journalière (par mois)")
    fig_month = analyse.plot_month(year=year, month=month, rep=trajet_type)
    st.pyplot(fig_month)

    # Afficher le graphique annuel
    st.header("📈 Évolution annuelle")
    fig_year = analyse.plot_year(year=year, rep=trajet_type)
    st.pyplot(fig_year)
else:
    st.warning("Veuillez charger les données pour afficher les résultats.")
