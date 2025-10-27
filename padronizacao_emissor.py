import re
import pandas as pd

# Função para substituir o emissor baseado nas keys
def substituir_emissor(emissor, df_keys_emissor):

    for _, row in df_keys_emissor.iterrows(): # para cada linha do dataframe que contém as chaves
        emissor_sem_espaco = emissor.strip() # remove todos os espaços antes e depois da string a ser verificada
        if re.search(row['KEYS'], emissor_sem_espaco, re.IGNORECASE): # se a string a ser verificada conter a palavra chave
            return row['EMISSOR'] # é atribuído o valor correto do emissor
    return 'N/A' # caso contrário, é dito como não categorizado

def buscar_risco(emissor,df_keys,df_risco):
    chaves_emissor = list(df_keys[df_keys['EMISSOR'] == emissor]['KEYS'])

    if emissor != 'N/A':
        for chave in range(len(chaves_emissor)):
            for linha in range(df_risco.shape[0]):
                if re.search(rf'\b{chaves_emissor[chave]}\b',df_risco['EMISSOR'].iloc[linha]):
                    return df_risco['GRAU DE RISCO'].iloc[linha]
    return 'N/A'

def verifica_codigo_emissor(emissor, df_codigos_emissor, caminho_df_codigos):
    df_codigos_emissor = df_codigos_emissor.fillna('N/A')

    if emissor in df_codigos_emissor.values:
        codigo = df_codigos_emissor.loc[df_codigos_emissor['EMISSOR'] == emissor, 'CÓDIGO'].values[0]
        return codigo

def ajuste_emissor(planilha_mestra,emissor_keys,instituicoes_bacen, caminho_emissor):
    planilha_mestra.columns = planilha_mestra.columns.str.upper()
    instituicoes_bacen = instituicoes_bacen.fillna('N/A')
    emissor_keys = emissor_keys.fillna('N/A')

    df_codigos_emissores = pd.read_excel(caminho_emissor)

    planilha_mestra = planilha_mestra.fillna('N/A')
    planilha_mestra['EMISSOR'] = planilha_mestra['EMISSOR'].str.strip()
    planilha_mestra['EMISSOR'] = planilha_mestra['EMISSOR'].astype(str)

    planilha_mestra['Emissores Corretos'] = planilha_mestra['EMISSOR'].apply(substituir_emissor, args=(emissor_keys,))
    planilha_mestra.drop(columns=['EMISSOR'], inplace=True)
    planilha_mestra.rename(columns={"Emissores Corretos": "EMISSOR"}, inplace=True)

    planilha_teste = planilha_mestra.copy()

    planilha_teste.loc[:, 'RISCO BACEN'] = planilha_teste['EMISSOR'].apply(buscar_risco,
                                                    args=(emissor_keys, instituicoes_bacen,))
    planilha_teste.loc[:, 'RISCO BACEN'] = planilha_teste['RISCO BACEN'].astype(str)

    planilha_teste['CÓDIGO'] = planilha_teste['EMISSOR'].apply(verifica_codigo_emissor,args = (df_codigos_emissores,caminho_emissor))

    planilha_teste['EMISSOR'] = planilha_teste['CÓDIGO']

    df_final = planilha_teste.drop(columns=['RISCO BACEN','CÓDIGO','VENCIMENTO','ORIGEM',]).copy()
    df_final = df_final.rename(columns={'CATEGORIA': 'CLASSIFICAÇÃO PORTFEL'}).reset_index().drop(columns='index')

    return df_final

