import pandas as pd
import re

def data_sb(data):
    # Filtrar ativos que contenham "CDB", "LCI" ou "LCA"
    filtro = data[data['broker'] == 'SMARTBRAIN']['asset_name'].str.contains(r'\b(CDB|LCI|LCA)\b', case=False, na=False)
    data_bancarios = data[data['broker'] == 'SMARTBRAIN'][filtro]
    return data_bancarios

# Função para processar cada string
def process_string(s):
  produto = s.split()[0]  # Primeiro termo (LCA ou CDB)
  banco = " ".join(s.split()[1:4]) if "BANCO" in s else ' '.join(s.split()[1:3])
  indexador = "IPCA" if "IPCA" in s else ("CDI" if "CDI" in s else "PRÉ")
  taxa = None
  vencimento = None
  grossup = 'SIM' if "GROSSUP*" in s else 'NÃO'

  # Extraindo taxa
  if "%" in s:
      taxa = s.split('%')[0].split()[-1] + '%'

  if "VENCTO:" in s:
      partes = s.split("VENCTO:")
      if len(partes) > 1 and partes[1].strip():  # Verifica se há algo após 'VENCTO:' e não está vazio
          vencimento = partes[1].split()[0]
      else:
          vencimento = None  # Ou algum valor padrão

  return {
      "Produto": produto,
      "Banco": banco,
      "Indexador": indexador,
      "Taxa": taxa,
      "Vencimento": vencimento,
      "GROSSUP": grossup
  }

def remover_numeros_caracteres_especiais(s):
  if s == 'BANCO C6':
    return 'BANCO C6'
  else:
    return re.sub(r'[^\w~´\s]|(?:\bCDI\b|\bIPCA\b)|\b\d+\b|\b\w\b', '', s, flags=re.UNICODE)

def limpar_taxa(s):    # Verifica se o valor é NaN ou não é uma string
    if pd.isna(s) or not isinstance(s, str):
        return None  # Retorna None para valores inválidos

    # Remover '+' ou '-' e o símbolo '%', mantendo os números e ponto
    taxa = re.sub(r'[^\d.-]', '', s)  # Remover tudo que não for dígito, ponto ou sinal
    if taxa:  # Verifica se a string resultante não está vazia
        return float(taxa)
    else:
        return None

def processa_emissores_SMARTBRAIN(dataset):
  # Seleção dos ativos provenientes da SMARTBRAIN
  data_formatado = dataset[dataset['broker']=='SMARTBRAIN']

  # Filtrar ativos que contenham "CDB", "LCI" ou "LCA"
  filtro = data_formatado['asset_name'].str.contains(r'\b(CDB|LCI|LCA)\b', case=False, na=False)
  data_bancarios = data_formatado[filtro]

  # Padronização do separador decimal
  data_bancarios_assets = data_bancarios['asset_name'].str.replace(',','.')

  strings = data_bancarios_assets.tolist()
  # Processar todas as strings
  dados = [process_string(s) for s in strings]
  # Criar o DataFrame
  df_organizado = pd.DataFrame(dados)

  # Tratamento final
  df_organizado['Banco'] = df_organizado['Banco'].apply(remover_numeros_caracteres_especiais)
  df_organizado['Taxa'] = df_organizado['Taxa'].fillna('').apply(limpar_taxa)

  return df_organizado
