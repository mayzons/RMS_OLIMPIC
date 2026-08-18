import os
import re
import sqlite3
import unicodedata
from datetime import datetime

import pandas as pd
from utils.caminhos import PASTA_GRAFANA, PASTA_TRATAR
from utils.logs_escrita import log_error, log_info


def tratar_nome_coluna(col_name: str) -> str:
  """Remove acentos, caracteres especiais, espaços extras e converte para snake_case."""
  texto = str(col_name).strip()
  texto = (
      unicodedata.normalize('NFKD', texto)
      .encode('ASCII', 'ignore')
      .decode('utf-8')
  )
  texto = re.sub(r'[^a-zA-Z0-9]+', '_', texto)
  return texto.lower().strip('_')


def grafana():
  pasta_arquivos = os.listdir(PASTA_TRATAR)

  arquivos_ok = [a for a in pasta_arquivos if 'grafana' in a.lower()]

  if not arquivos_ok:
    log_info('Nenhum arquivo Grafana encontrado para processar.')
    return

  for arquivo in arquivos_ok:
    caminho_arquivo = os.path.join(PASTA_TRATAR, arquivo)
    nome, extensao = os.path.splitext(arquivo)

    print(caminho_arquivo)
    print(arquivo)
    # 1. Carregar o arquivo dinâmico da iteração
    df = pd.read_excel(caminho_arquivo)

    # 2. Tratar e mapear os nomes das colunas
    colunas_originais = df.columns.tolist()
    df.columns = [tratar_nome_coluna(col) for col in df.columns]

    print('\n=== Mapeamento de Colunas ===')
    for orig, nova in zip(colunas_originais, df.columns):
      # print(f"  • '{orig}' ➔ '{nova}'")
      ...

    # 3. Filtra Serviço
    # CERTIFIQUE-SE de substituir 'tipo_de_servico' pelo nome correto da coluna tratada
    coluna_servico = (
        'tipo_de_servico'
    )

    servicos_desejados = [
        'Abastece',
        'Drive Thru',
        'Concessionárias',
        'Estacionamentos Automatizados',
    ]

    if coluna_servico in df.columns:
      df_filtrado = df[df[coluna_servico].isin(servicos_desejados)]

    df_filtrado['data_atualizacao'] = datetime.now()

    # 4. Inserção SQLite (descomente quando validar os prints)
    CAMINHO = ''
    nome_banco = os.path.join(PASTA_GRAFANA, 'dados_opc.db')
    nome_tabela = 'tb_opc'
    with sqlite3.connect(nome_banco) as conn:
        df_filtrado.to_sql(name=nome_tabela, con=conn,
                           if_exists='replace', index=False)

    os.system(f'del "{caminho_arquivo}"')
