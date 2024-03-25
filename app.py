import streamlit as st 
from funcoes import *

html_text = """
<h1 style='color: blue;'>Projeto Estacas</h1>
<h2 style='color: green;'>Cabeçalho</h2>
<p align="justify">
<p>Lorem ipsum dolor sit amet. Qui voluptas odio ea blanditiis quae non numquam internos sed Quis repudiandae qui expedita sint.
Quo animi consectetur ea officia voluptate et delectus totam cum amet veniam! Non quod incidunt sed rerum vitae ea soluta libero.
Sit delectus quibusdam et nulla galisum sed esse assumenda.</p>
</a>
"""

# Renderizar o texto HTML
st.markdown(html_text, unsafe_allow_html=True)

df, nome = carregar_dados()

if df is not None:
    diametro, f_ck, tipo = estaca_info()
    novo_df = capacidade_carga(df, diametro, f_ck, tipo)
    download_excel(novo_df, nome)
