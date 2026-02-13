import streamlit as st
import pandas as pd
import os

st.title("Cuadro de scrapeo de los seguidores")

# Ruta absoluta para encontrar el archivo sin importar desde dónde se ejecute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "instagram_scraper", "resultados.csv")

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    st.dataframe(df)
else:
    st.error("No se encontró el archivo resultados.csv")