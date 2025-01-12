import pandas as pd
from datetime import datetime
import streamlit as st
from api.fetch_data_tgvmax import fetch_data_with_csv_cache
from analysis.indicators import TrajetAnalyse
def process_validation(departure,arrival,col1,col2,col3):

    # cache checking

    df_cache=pd.read_csv('data/cache_log.csv')
    fetch_data_with_csv_cache(departure,arrival)
    file_path="data/cache/LYON_(intramuros)_to_PARIS.csv"

    trajet=TrajetAnalyse(file_path)
    with col1:
        st.title("Evolution du nombre de trajets dispos")
        st.pyplot(trajet.plot_year())
    with col2:
        st.title("Camembert")
        st.pyplot(trajet.camembert())
    


    
    



    