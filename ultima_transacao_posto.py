from utils.caminhos import (
    PASTA_DESTINO, ARQUIVO_CONTROLE,
    USER, PASSWORD, DNS, PORT, SERVICE, ORACLE_HOME
)
import os
import pandas as pd
from utils.logs_escrita import log_info, log_error
import oracledb as cx_Oracle
import json
from datetime import datetime, timedelta


def converter_data_mista(serie):
    """
    Converte datas em formato misto: DD/MM/YYYY ou MM/DD/YYYY.
    """
    br = pd.to_datetime(serie, errors="coerce", dayfirst=True)
    us = pd.to_datetime(serie, errors="coerce", dayfirst=False)
    return br.combine_first(us)


def trn():

    log_info("Iniciado o select no Oracle para Autorizações!")

    try:

        # Configura Oracle Instant Client
        oracle_instant_client_dir = ORACLE_HOME
        os.environ["PATH"] = f"{oracle_instant_client_dir};{os.environ['PATH']}"  # NOQA

        if not cx_Oracle.clientversion():
            cx_Oracle.init_oracle_client(lib_dir=oracle_instant_client_dir)

        # Conexão
        conexao = cx_Oracle.connect(
            user=USER,
            password=PASSWORD,
            dsn=f"{DNS}:{PORT}/{SERVICE}"
        )

        cursor = conexao.cursor()

        sql = """
            SELECT
            TB0008_CD_CONVENIADO AS Posto,
            TO_CHAR(MAX(tb0153_dt_transacao), 'YYYY-MM-DD HH24:MI:SS') AS UltimaTransacao
            FROM
                CADMO.tb0153_transacaoconveniado
            WHERE
                tb0153_dt_transacao >= SYSDATE - 90
                AND tb0138_cd_produto = 1
            GROUP BY
                TB0008_CD_CONVENIADO
        """

        cursor.execute(sql)

        rows = cursor.fetchall()

        # nomes das colunas
        colunas = [desc[0] for desc in cursor.description]

        # transforma em dataframe
        df = pd.DataFrame(rows, columns=colunas)

        cursor.close()
        conexao.close()

        log_info(f"O Select retornou {len(df)} Autorizações!")

        # Tratamento de data
        if "DATA" in df.columns:
            df["DATA"] = converter_data_mista(df["DATA"])
            df["DATA"] = df["DATA"].dt.strftime("%Y-%m-%d %H:%M")
            log_info("Coluna DATA tratada com sucesso.")

        # Renomeia colunas padrão
        df.columns = ["CREDENCIADO", "DATA"]

        # Caminho do arquivo
        caminho_csv = os.path.join(PASTA_DESTINO, "transacoes.csv")

        # Exporta CSV
        df.to_csv(
            caminho_csv,
            sep=",",
            index=False,
            encoding="utf-8"
        )

        log_info(f"CSV gerado com sucesso com {len(df)} registros!")
        return True

    except Exception as e:

        log_error(f"Erro ao processar transacoes: {str(e)}")
        return False


def carregar_controle():
    with open(ARQUIVO_CONTROLE, "r") as f:
        return json.load(f)


def salvar_controle(dados):
    with open(ARQUIVO_CONTROLE, "w") as f:
        json.dump(dados, f, indent=4)


def dentro_da_janela():
    agora = datetime.now()
    return 7 <= agora.hour < 20


def gatilho_trn():

    if not dentro_da_janela():
        log_info("Fora da janela (05-20). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_trn"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina TRN...")
        executar = True

        controle["proxima_execucao_trn"] = (
            agora + timedelta(hours=controle["horas_trn"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        try:
            trn()
            salvar_controle(controle)
            return True
        except Exception as e:
            log_error(f"Erro ao executar rotina TRN: {str(e)}")
            return False
    else:
        log_info("Ainda não chegou o horário da execução.")
