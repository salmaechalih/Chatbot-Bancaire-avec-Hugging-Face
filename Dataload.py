# app/main.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Téléversement CSV", layout="centered")

st.title("📂 Téléverser un fichier CSV")

# Zone d'upload
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Fichier chargé avec succès ! 🎉")
        st.write("Aperçu des données :")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
else:
    st.info("En attente du fichier CSV...")

