import numpy as np

# Tabelas de coeficientes livro Elementos de Fundações em Concreto
k_alpha = {'areia': [1, 0.40],
           'areia siltosa': [0.80, 2.00],
           'areia siltoargilosa': [0.70, 2.4],
           'areia argilosa': [0.60, 3.00],
           'areia argilosiltosa': [0.50, 2.80],
           'silte': [0.40, 3.00],
           'silte arenoso': [0.55, 2.2],
           'silte arenoargiloso': [0.45, 2.8],
           'silte argiloso': [0.23, 3.4],
           'silte argiloarenoso': [0.25, 3.00],
           'argila': [0.20, 6.00],
           'argila arenosa': [0.35, 2.4],
           'argila arenosiltosa': [0.30, 2.8],
           'argila siltosa': [0.22, 4.0],
           'argila siltoarenosa': [0.33, 3.00]
          }

c = {'argila': 120,
    'silte argiloso': 200,
           'silte arenoso': 250,
           'areia': 400
          }

f_1 = {'franki': 2.5, 'metálica': 1.75, 'pré-moldada de concreto': 1.75, 'escavada': 3.00}

# Funções de projeto
def area_estaca(linha):
    diametro = linha['diâmetro (m)']
    area = (np.pi * diametro ** 2) / 4
    return area


def perimetro_estaca(linha):
    diametro = linha['diâmetro (m)']
    perimetro = np.pi * diametro
    return perimetro


def k_solo(linha, coeficiente_k_e_alpha):
    solo = linha['Solo Aoki-Veloso']
    for chave, valor in coeficiente_k_e_alpha.items():
        if solo == chave:
           k = valor[0]
           break
    return k


def c_solo(linha, coeficiente_c):
    solo = linha['Solo Decourt-Quaresma']
    for chave, valor in coeficiente_c.items():
        if solo == chave:
           c = valor
           break
    return c


def alpha_solo(linha, coeficiente_k_e_alpha):
    solo = linha['Solo Aoki-Veloso']
    for chave, valor in coeficiente_k_e_alpha.items():
        if solo == chave:
           alpha = valor[1]
           break
    return alpha


def f1(linha, f_1):
    tipo_estaca = linha['tipo estaca']
    for chave, valor in f_1.items():
        if tipo_estaca == chave:
            f_1 = valor
            break
    return f_1


def tensao_ponta(linha):
    return linha['NSPT'] * linha['k'] / linha['f_1'] * 1000


def carga_ponta(linha):
    return linha['r_p (kPa)'] * linha['area estaca (m2)']


def tensao_lateral(linha):
    tal_lk = linha['alpha'] * linha['k'] * linha['NSPT'] / linha['f_2']
    return tal_lk * linha['perimetro estaca (m)'] * 1 * 1000


def carga_lateral(linha):
    return linha['r_l (kPa)'] * linha['area estaca (m2)']


def carga_total(linha):
    return linha['r_rd [Aoki-Veloso] (kPa)'] * linha['area estaca (m2)']