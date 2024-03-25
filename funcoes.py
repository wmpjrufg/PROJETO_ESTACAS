import streamlit as st
import pandas as pd
import tempfile
from estacas import *

def carregar_dados():
    uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.subheader("Base de dados inicial:")
            st.dataframe(df)
            nome_df = uploaded_file.name
            
            # Verifique se o DataFrame tem todas as colunas necessárias
            colunas_necessarias = ['profundidade (m)', 'NSPT', 'diâmetro (m)', 'Solo', 'Solo Aoki-Veloso', 'Solo Decourt-Quaresma']
            # Verifica se todas as colunas necessárias estão presentes no DataFrame
            colunas_ausentes = [coluna for coluna in colunas_necessarias if coluna not in df.columns]
            
            if colunas_ausentes:
                raise ValueError(f"colunas ausentes: {', '.join(colunas_ausentes)}")
            
            return df, nome_df # Retornando o DataFrame 
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o arquivo: {str(e)}")
            return None, None  # Retornando None em caso de erro
    
    else:
        st.warning("Por favor, faça o upload de um arquivo Excel.")
        return None, None
    
        
def estaca_info():
    st.title("Informações da Estaca")
    
    diametro_estaca = st.number_input("Digite o diâmetro da estaca em metros:", min_value=0.0)
    f_ck = st.number_input("Digite a tensão de compressão característica do concreto (kPa):", min_value=0.0)
    tipo_estaca = st.selectbox("Selecione o tipo da estaca:", ["Franki", "Metálica", "Pré-moldada de concreto", "Escavada"])
    if st.button('Adicionar Informações'):
        return diametro_estaca, f_ck, tipo_estaca.lower()

    else:
        return None, None, None


def capacidade_carga(df, diametro_estaca, f_ck, tipo_estaca):
    try: 
        if diametro_estaca is not None and tipo_estaca is not None:
            st.title("Capacidade de Carga")
            df['tipo estaca'] = tipo_estaca.lower()
            df['area estaca (m2)'] = df.apply(area_estaca, axis=1)
            df['perimetro estaca (m)'] = df.apply(perimetro_estaca, axis=1)
            df['k'] = df.apply(k_solo, axis=1)
            df['alpha'] = df.apply(alpha_solo, axis=1)
            df['f_1'] = df.apply(f1, axis=1)
            df['f_2'] = 2 * df['f_1']
            df['r_p [Aoki-Veloso] (kPa)'] = df.apply(tensao_ponta_aoki_veloso, axis=1)
            df['P_p [Aoki-Veloso] (kN)'] = df.apply(carga_ponta_aoki_veloso, axis=1)
            df['r_l [Aoki-Veloso] (kPa)'] = df.apply(tensao_lateral_aoki_veloso, axis=1)
            soma_resultados = []
            r_l = df['r_l [Aoki-Veloso] (kPa)'].to_list()
            for i in range(len(df)):
                if i == 0:
                    soma = df.iloc[i]['r_l [Aoki-Veloso] (kPa)']
                else:
                    soma = sum(r_l[:i+1])
                soma_resultados.append(soma)
            df['r_l acumulado [Aoki-Veloso] (kPa)'] = soma_resultados
            df['P_l [Aoki-Veloso] (kN)'] = df.apply(carga_lateral_aoki_veloso, axis=1)
            df['r_rd [Aoki-Veloso] (kPa)'] = df['r_l acumulado [Aoki-Veloso] (kPa)'] + df['r_p [Aoki-Veloso] (kPa)']
            df['P_rd [Aoki-Veloso] (kN)'] = df['P_p [Aoki-Veloso] (kN)'] + df['P_l [Aoki-Veloso] (kN)']
            df['c'] = df.apply(c_solo, axis=1)
            df['r_p [Decourt-Quaresma] (kPa)'] = df.apply(tensao_ponta_decorto_quaresma, axis=1)
            df['P_p [Decourt-Quaresma] (kN)'] = df.apply(carga_ponta_decourt_quaresma, axis=1)
            n_spt = df['NSPT'].to_list()
            soma_resultados = []
            for i in range(len(df)):
                if i == 0:
                    soma = df.iloc[i]['NSPT']
                else:
                    soma = sum(n_spt[:i+1]) / (i+1)
                soma_resultados.append(soma)
            df['nspt_medio'] = soma_resultados
            df['r_l acumulado [Decourt-Quaresma] (kPa)'] = df.apply(tensao_lateral_decourt_quaresma, axis=1)
            df['P_l [Decourt-Quaresma] (kN)'] = df.apply(carga_lateral_decourt_quaresma, axis=1)
            df['r_rd [Decourt-Quaresma] (kPa)'] = df['r_l acumulado [Decourt-Quaresma] (kPa)'] + df['r_p [Decourt-Quaresma] (kPa)']
            df['P_rd [Decourt-Quaresma] (kN)'] = df['P_p [Decourt-Quaresma] (kN)'] + df['P_l [Decourt-Quaresma] (kN)']
            
            df['P_rd (kN)'] = df[['P_rd [Decourt-Quaresma] (kN)', 'P_rd [Aoki-Veloso] (kN)']].min(axis=1)
            df['f_cd (kPa)'] = f_ck / 3.1
            df['P_Rd (kN)'] = 0.85 * df['f_cd (kPa)'] * df['area estaca (m2)']
            st.write(df)
            return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar a tabela: {str(e)}")


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
