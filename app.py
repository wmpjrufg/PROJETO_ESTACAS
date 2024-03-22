import streamlit as st 
from funcoes import *

df, nome = carregar_dados()

if df is not None:
    diametro, tipo = estaca_info()
    novo_df = capacidade_carga(df, diametro, tipo)
    download_excel(novo_df, nome)
