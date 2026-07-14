import sys
import os
import pandas as pd
import sqlite3
from utils.logs_escrita import log_info, log_error
from utils.caminhos import CONSUMO_NATA, BANCO_DADOS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def insere_abertos(cam):
    try:
        arquivo_excel = cam
        tabela = "CHAMADOS_ABERTOS"
        log_info(f"Processando arquivo: {arquivo_excel}")

        df = pd.read_excel(arquivo_excel)

        colunas_padrao = [
            "NUMERO", "TIPO_TAREFA", "TYPE_WO", "ESTADO_CHAMADO",
            "TIPO_CONTATO", "ENCERRADO_POR", "CODIGO", "EMPRESA",
            "MODELO", "ABERTO", "ENCERRADO", "SUBESTADO",
            "DESCRICAO_RESUMIDA", "DESCRICAO", "GRUPO_DESIGNADO",
            "CAUSA_ERRO", "CLOSE_CODE", "ANOTACOES_FECHAMENTO",
            "VIP", "VERSAO_SOLUCAO", "INTEGRATION_ID",
            "ITEM_CONFIGURACAO", "ATRIBUIDO_A", "INCIDENTE_PRIMARIO",
            "INICIO_REAL_TRABALHO", "TERMINO_REAL_TRABALHO",
            "ID", "HISTORICO_IDS", "CONTAGEM_REATRIBUICOES",
            "ATUALIZACOES", "SERVICO_NEGOCIO", "ESTADO", "CIDADE",
            "RUA", "QUANTIDADE_PISTAS", "REDE", "ATUALIZADO_EM",
            "ATUALIZADO_POR", "OPC", "TENTATIVAS_CONTATO",
            "ABERTO_POR", "GRUPO_EXPEDICAO", "IBM", "TIPO_OPERACAO",
            "DATE_SENT_THE_GROUP", "DATA_ARQUIVO", "ARQUIVO_ORIGINAL",
            "CODIGO_TRATADO"
        ]

        df.columns = colunas_padrao

        DATA_ARQUIVO = df["DATA_ARQUIVO"].iloc[0]

        log_info(f"Data encontrada no arquivo: {DATA_ARQUIVO}")

        # SQLITE
        conn = sqlite3.connect(BANCO_DADOS)
        cursor = conn.cursor()

        # APAGA DA BASE SE JÁ TIVER REGISTRO COM A MESMA DATA
        cursor.execute(f"""
        DELETE FROM {tabela} WHERE DATA_ARQUIVO = ? """, (DATA_ARQUIVO,))

        conn.commit()

        log_info("Registros antigos removidos")

        # inserir dados novos
        df.to_sql(tabela, conn, if_exists="append", index=False)

        # FECHA CONEXÃO
        conn.close()

        log_info("Dados inseridos com sucesso!")
        return True
    except Exception as e:
        log_error(f"Erro: {e}")
        return False


def insere_encerrados(cam):
    try:
        arquivo_excel = cam
        tabela = "CHAMADOS_ENCERRADOS"
        log_info(f"Processando arquivo: {arquivo_excel}")

        df = pd.read_excel(arquivo_excel)

        colunas_padrao = [
            "NUMERO", "TIPO_TAREFA", "TYPE_WO", "ESTADO_CHAMADO",
            "TIPO_CONTATO", "ENCERRADO_POR", "CODIGO", "EMPRESA",
            "MODELO", "ABERTO", "ENCERRADO", "SUBESTADO",
            "DESCRICAO_RESUMIDA", "DESCRICAO", "GRUPO_DESIGNADO",
            "CAUSA_ERRO", "CLOSE_CODE", "ANOTACOES_FECHAMENTO",
            "VIP", "VERSAO_SOLUCAO", "INTEGRATION_ID",
            "ITEM_CONFIGURACAO", "ATRIBUIDO_A", "INCIDENTE_PRIMARIO",
            "INICIO_REAL_TRABALHO", "TERMINO_REAL_TRABALHO",
            "ID", "HISTORICO_IDS", "CONTAGEM_REATRIBUICOES",
            "ATUALIZACOES", "SERVICO_NEGOCIO", "ESTADO", "CIDADE",
            "RUA", "QUANTIDADE_PISTAS", "REDE", "ATUALIZADO_EM",
            "ATUALIZADO_POR", "OPC", "TENTATIVAS_CONTATO",
            "ABERTO_POR", "GRUPO_EXPEDICAO", "IBM", "TIPO_OPERACAO",
            "DATE_SENT_THE_GROUP", "DATA_ARQUIVO", "ARQUIVO_ORIGINAL",
            "CODIGO_TRATADO"
        ]

        df.columns = colunas_padrao

        DATA_ARQUIVO = df["DATA_ARQUIVO"].iloc[0]

        log_info(f"Data encontrada no arquivo: {DATA_ARQUIVO}")

        # SQLITE
        conn = sqlite3.connect(BANCO_DADOS)
        cursor = conn.cursor()

        # APAGA DA BASE SE JÁ TIVER REGISTRO COM A MESMA DATA
        cursor.execute(f"""
        DELETE FROM {tabela} WHERE DATA_ARQUIVO = ? """, (DATA_ARQUIVO,))

        conn.commit()

        log_info("Registros antigos removidos")

        # inserir dados novos
        df.to_sql(tabela, conn, if_exists="append", index=False)

        # FECHA CONEXÃO
        conn.close()

        log_info("Dados inseridos com sucesso!")
        return True
    except Exception as e:
        log_error(f"Erro: {e}")
        return False


def nata_execucao():
    QTD_ARQUIVOS = len(
        [f for f in os.listdir(CONSUMO_NATA) if f.endswith('.xlsx')])
    log_info(f"Quantidade de arquivos a serem processados: {QTD_ARQUIVOS}")

    while QTD_ARQUIVOS > 0:
        arquivos = os.listdir(CONSUMO_NATA)
        for a in arquivos:
            # if a == "abertos.xlsx":
            if "aberto" in a.lower() or "abt hoje a" in a.lower():
                cam = os.path.join(CONSUMO_NATA, a)
                insere_abertos(cam)
                QTD_ARQUIVOS -= 1

                os.system(f'del "{cam}"')

            elif "encerrado" in a.lower() or "abt hoje e" in a.lower():
                cam = os.path.join(CONSUMO_NATA, a)
                insere_encerrados(cam)
                QTD_ARQUIVOS -= 1
                os.system(f'del "{cam}"')

            else:
                log_info(f"Arquivo {a} não é o esperado e será ignorado.")
                QTD_ARQUIVOS -= 1
