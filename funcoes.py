import streamlit as st
import pandas as pd
import tempfile
from estacas import *

def carregar_dados():
    st.title("Projeto Estacas")

    uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.subheader("Base de dados inicial:")
            st.dataframe(df)
            nome_df = uploaded_file.name
            return df, nome_df # Retornando o DataFrame para que possa ser utilizado em outras partes do código
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o arquivo: {str(e)}")
            return None, None  # Retornando None em caso de erro
    
    else:
        st.warning("Por favor, faça o upload de um arquivo Excel.")
        return None, None
        
def estaca_info():
    st.title("Informações da Estaca")
    
    diametro_estaca = st.number_input("Digite o diâmetro da estaca em metros:", min_value=0.0)
    tipo_estaca = st.selectbox("Selecione o tipo da estaca:", ["Franki", "Metálica", "Pré-moldada de concreto", "Escavada"])

    if st.button('Adicionar Informações'):
        return diametro_estaca, tipo_estaca.lower()

    else:
        return None, None


def capacidade_carga(df, diametro_estaca, tipo_estaca):
    if diametro_estaca is not None and tipo_estaca is not None:
        st.title("Capacidade de Carga")
        df['tipo estaca'] = tipo_estaca
        df['diâmetro (m)'] = diametro_estaca
        df['area estaca (m2)'] = df.apply(area_estaca, axis=1)
        df['perimetro estaca (m)'] = df.apply(perimetro_estaca, axis=1)
        df['k'] = df.apply(k_solo, axis=1, args=(k_alpha,))
        df['alpha'] = df.apply(alpha_solo, axis=1, args=(k_alpha,))
        df['f_1'] = df.apply(f1, axis=1, args=(f_1,))
        df['f_2'] = 2 * df['f_1']
        df['r_p (kPa)'] = df.apply(tensao_ponta, axis=1)
        df['P_p (kN)'] = df.apply(carga_ponta, axis=1)
        df['r_l (kPa)'] = df.apply(tensao_lateral, axis=1)
        df['P_l (kN)'] = df.apply(carga_lateral, axis=1)
        soma_resultados = []
        r_l = df['r_l (kPa)'].to_list()
        for i in range(len(df)):
            if i == 0:
                soma = df.iloc[i]['r_p (kPa)'] + df.iloc[i]['r_l (kPa)']
            else:
                soma = df.iloc[i]['r_p (kPa)'] + sum(r_l[:i+1])
            soma_resultados.append(soma)
        df['r_rd [Aoki-Veloso] (kPa)'] = soma_resultados
        df['P_rd [Aoki-Veloso] (kN)'] = df.apply(carga_total, axis=1)
        st.write(df)
        return df


def download_excel(df, nome_df):
    if df is not None:
        excel_file_name = nome_df.split(".")[0] + "_copia.xlsx"

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with pd.ExcelWriter(tmp.name, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)

            tmp.flush()

            with open(tmp.name, 'rb') as f:
                excel_file_content = f.read()

        st.download_button(
            label='Download Excel',
            data=excel_file_content,
            file_name=excel_file_name,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )