import oracledb as cx_Oracle
import sqlite3
import os
import json
from datetime import datetime, timedelta
import csv
from utils.logs_escrita import (log_info, log_error)
from utils.caminhos import (PASTA_ROOT, USER, PASSWORD, DNS, ARQUIVO_CONTROLE,
                            PORT, SERVICE, ORACLE_HOME, PASTA_DESTINO)

BANCO_ROOT = os.path.join(PASTA_ROOT, r"DATA\\banco_base.db")


def executa():
    autorizacao = []

    log_info('Iniciado o select no Oracle para Transações!')

    oracle_instant_client_dir = ORACLE_HOME
    os.environ["PATH"] = f"{oracle_instant_client_dir};{os.environ['PATH']}"

    # Inicializa o cliente primeiro, tratando caso já tenha sido carregado na memória
    try:
        cx_Oracle.init_oracle_client(lib_dir=oracle_instant_client_dir)
    except Exception:
        pass  # Já foi inicializado anteriormente no processo

    def conexaoDB():
        conn = cx_Oracle.connect(
            user=USER,
            password=PASSWORD,
            dsn=f'{DNS}:{PORT}/{SERVICE}'
        )
        return conn

    conexao = conexaoDB()
    resultado = conexao.cursor()

    sql = """
    SELECT 
        TB0008_CD_CONVENIADO AS POSTO,
        TO_CHAR(TB0110_DT_PEDIDOAUTORIZACAO, 'DD/MM/YYYY HH24:MI:SS') AS DATA,
        TB0110_ID_DISPOSITIVO AS DISPOSITIVO,
        TB0110_NR_PLACAVEICULO AS PLACA,
        TB0110_FL_RESULTADO AS RESULTADO,
        TB0025_CL_CDMOTIVOREJEICAO AS "COD_REJEICAO",
        TB0025_CD_MOTIVOREJEICAO AS "MOT_REJEICAO",
        TB0110_CD_TOKEN AS TP_SOLICITACAO,
        TB0110_VL_SALDODISPONIVEL AS SALDO,
        TB0110_VL_SALDODIARIODISP AS SALDO_DIARIO
    FROM CADMO.TB0110_AUTORIZACAO
    WHERE TB0110_DT_PEDIDOAUTORIZACAO >= SYSDATE - 1
    AND TO_CHAR(TB0110_DT_PEDIDOAUTORIZACAO, 'HH24:MI') >= '08:00'
    AND TO_CHAR(TB0110_DT_PEDIDOAUTORIZACAO, 'HH24:MI') <= '18:00'
    AND TB0025_CD_TIPO = 3
    """

    resultado.execute(sql)
    rows = resultado.fetchall()

    autorizacao.clear()
    autorizacao.extend(rows)

    resultado.close()
    conexao.close()

    log_info(f'O Select retornou {len(autorizacao)} Autorizações!')

    return autorizacao


def exportar_para_csv(result):
    autorizacao = result
    autorizacao_encontradas = []
    autorizacao_nao_encontradas = []

    log_info('Iniciando o cruzamento e exportação das autorizações!')

    # 1. Garante que o diretório 'DATA' existe no servidor
    pasta_banco = os.path.dirname(BANCO_ROOT)
    os.makedirs(pasta_banco, exist_ok=True)

    conexao = sqlite3.connect(BANCO_ROOT)
    cursor = conexao.cursor()

    # 2. Cria a tabela ANTES de tentar buscar os registros (evita erro de tabela inexistente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autorizacao_sincronizada (
            TP_SOLICITACAO TEXT PRIMARY KEY,
            DATA_SINCRONISMO TEXT
        )
    """)
    conexao.commit()

    # 3. Busca tokens já sincronizados
    cursor.execute("SELECT TP_SOLICITACAO FROM autorizacao_sincronizada")
    sincronizado = {str(row[0]).strip() for row in cursor.fetchall()}

    # 4. Separa autorizações pendentes
    for t in autorizacao:
        tp_solicitacao = str(t[7]).strip() if t[1] is not None else ""
        if tp_solicitacao in sincronizado:
            autorizacao_encontradas.append(t)
        else:
            autorizacao_nao_encontradas.append(t)

    log_info(f"Encontradas (já sincronizadas): {len(autorizacao_encontradas)}")
    log_info(f"Não encontradas (pendentes): {len(autorizacao_nao_encontradas)}")

    # 5. Gera CSV de pendentes e atualiza o controle no SQLite
    if autorizacao_nao_encontradas:
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        caminho_csv = os.path.join(PASTA_DESTINO, "autorizacoes_pendentes.csv")

        with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo_csv:
            writer = csv.writer(arquivo_csv, delimiter=",")
            writer.writerow(["POSTO", "DATA", "DISPOSITIVO", "PLACA", "RESULTADO", "COD_REJEICAO", "MOT_REJEICAO", "TP_SOLICITACAO", "SALDO", "SALDO_DIARIO"])
            writer.writerows(autorizacao_nao_encontradas)

        log_info(f'CSV gerado com sucesso em: {caminho_csv}')

        data_sincronismo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        novos_sincronizados = [
            (str(t[7]).strip(), data_sincronismo) 
            for t in autorizacao_nao_encontradas 
            if t[7] is not None
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO autorizacao_sincronizada (TP_SOLICITACAO, DATA_SINCRONISMO)
            VALUES (?, ?)
        """, novos_sincronizados)

        conexao.commit()
        log_info(f'{len(novos_sincronizados)} novas autorizações gravadas na tabela autorizacao_sincronizada!')
    else:
        log_info('Nenhuma autorização pendente para exportar ou gravar.')

    cursor.close()
    conexao.close()


def carregar_controle():
    with open(ARQUIVO_CONTROLE, "r") as f:
        return json.load(f)


def salvar_controle(dados):
    with open(ARQUIVO_CONTROLE, "w") as f:
        json.dump(dados, f, indent=4)


def dentro_da_janela():
    agora = datetime.now()
    return 5 <= agora.hour < 22


def autorizacao_historico():

    if not dentro_da_janela():
        log_info("Fora da janela (05-22). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_authist"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina AUT Historico...")
        executar = True

        controle["proxima_execucao_authist"] = (
            agora + timedelta(hours=controle["horas_authist"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        try:
            autorizacoes = executa()
            exportar_para_csv(autorizacoes)
            salvar_controle(controle)
            return True

        except Exception as e:
            log_error(f"Erro ao executar rotina AUT Historico: {str(e)}")
            return False

    else:
        log_info("Ainda não chegou o horário da execução.")

# import csv
# import json
# import os
# import sqlite3
# from datetime import datetime, timedelta

# import oracledb as cx_Oracle
# from utils.caminhos import (
#     ARQUIVO_CONTROLE,
#     DNS,
#     ORACLE_HOME,
#     PASSWORD,
#     PASTA_DESTINO,
#     PASTA_ROOT,
#     PORT,
#     SERVICE,
#     USER,
# )
# from utils.logs_escrita import log_error, log_info

# BANCO_ROOT = os.path.join(PASTA_ROOT, r"DATA\banco_base.db")


# # 1. Recebe a data como parâmetro (ex: datetime.date ou str 'YYYY-MM-DD')
# def executa(data_alvo):
#     autorizacao = []

#     data_str = data_alvo.strftime("%Y-%m-%d")
#     log_info(f"Iniciado o select no Oracle para a data: {data_str}")

#     oracle_instant_client_dir = ORACLE_HOME
#     os.environ["PATH"] = f"{oracle_instant_client_dir};{os.environ['PATH']}"

#     try:
#         cx_Oracle.init_oracle_client(lib_dir=oracle_instant_client_dir)
#     except Exception:
#         pass

#     def conexaoDB():
#         return cx_Oracle.connect(
#             user=USER, password=PASSWORD, dsn=f"{DNS}:{PORT}/{SERVICE}"
#         )

#     conexao = conexaoDB()
#     resultado = conexao.cursor()

#     # 2. Ajuste na SQL para buscar exatamente as transações do dia informado entre 08:00 e 18:00
#     sql = """
#     SELECT 
#         TB0008_CD_CONVENIADO AS POSTO,
#         TO_CHAR(TB0110_DT_PEDIDOAUTORIZACAO, 'DD/MM/YYYY HH24:MI:SS') AS DATA,
#         TB0110_ID_DISPOSITIVO AS DISPOSITIVO,
#         TB0110_NR_PLACAVEICULO AS PLACA,
#         TB0110_FL_RESULTADO AS RESULTADO,
#         TB0025_CL_CDMOTIVOREJEICAO AS "COD_REJEICAO",
#         TB0025_CD_MOTIVOREJEICAO AS "MOT_REJEICAO",
#         TB0110_CD_TOKEN AS TP_SOLICITACAO,
#         TB0110_VL_SALDODISPONIVEL AS SALDO,
#         TB0110_VL_SALDODIARIODISP AS SALDO_DIARIO
#     FROM CADMO.TB0110_AUTORIZACAO
#     WHERE TB0110_DT_PEDIDOAUTORIZACAO >= TO_DATE(:dt_inicio, 'YYYY-MM-DD HH24:MI:SS')
#       AND TB0110_DT_PEDIDOAUTORIZACAO <= TO_DATE(:dt_fim, 'YYYY-MM-DD HH24:MI:SS')
#       AND TB0025_CD_TIPO = 3
#     """

#     dt_inicio = f"{data_str} 08:00:00"
#     dt_fim = f"{data_str} 18:00:00"

#     resultado.execute(sql, dt_inicio=dt_inicio, dt_fim=dt_fim)
#     rows = resultado.fetchall()

#     autorizacao.clear()
#     autorizacao.extend(rows)

#     resultado.close()
#     conexao.close()

#     log_info(
#         f"O Select para {data_str} retornou {len(autorizacao)} Autorizações!"
#     )
#     return autorizacao


# # 3. Recebe a data para dinamizar o nome do arquivo CSV gerado
# def exportar_para_csv(result, data_alvo):
#     autorizacao = result
#     autorizacao_encontradas = []
#     autorizacao_nao_encontradas = []

#     log_info(
#         f"Iniciando o cruzamento e exportação para {data_alvo.strftime('%Y-%m-%d')}!"
#     )

#     pasta_banco = os.path.dirname(BANCO_ROOT)
#     os.makedirs(pasta_banco, exist_ok=True)

#     conexao = sqlite3.connect(BANCO_ROOT)
#     cursor = conexao.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS autorizacao_sincronizada (
#             TP_SOLICITACAO TEXT PRIMARY KEY,
#             DATA_SINCRONISMO TEXT
#         )
#     """)
#     conexao.commit()

#     cursor.execute("SELECT TP_SOLICITACAO FROM autorizacao_sincronizada")
#     sincronizado = {str(row[0]).strip() for row in cursor.fetchall()}

#     for t in autorizacao:
#         tp_solicitacao = str(t[7]).strip() if t[7] is not None else ""
#         if tp_solicitacao in sincronizado:
#             autorizacao_encontradas.append(t)
#         else:
#             autorizacao_nao_encontradas.append(t)

#     # 4. Cria arquivo único identificando a data (ex: autorizacoes_2026-03-01.csv)
#     if autorizacao_nao_encontradas:
#         os.makedirs(PASTA_DESTINO, exist_ok=True)

#         nome_arquivo = f"autorizacoes_{data_alvo.strftime('%Y-%m-%d')}.csv"
#         caminho_csv = os.path.join(PASTA_DESTINO, nome_arquivo)

#         with open(
#             caminho_csv, mode="w", newline="", encoding="utf-8"
#         ) as arquivo_csv:
#             writer = csv.writer(arquivo_csv, delimiter=",")
#             writer.writerow([
#                 "POSTO",
#                 "DATA",
#                 "DISPOSITIVO",
#                 "PLACA",
#                 "RESULTADO",
#                 "COD_REJEICAO",
#                 "MOT_REJEICAO",
#                 "TP_SOLICITACAO",
#                 "SALDO",
#                 "SALDO_DIARIO",
#             ])
#             writer.writerows(autorizacao_nao_encontradas)

#         log_info(f"CSV gerado com sucesso em: {caminho_csv}")

#         data_sincronismo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         novos_sincronizados = [
#             (str(t[7]).strip(), data_sincronismo)
#             for t in autorizacao_nao_encontradas
#             if t[7] is not None
#         ]

#         cursor.executemany(
#             """
#             INSERT OR IGNORE INTO autorizacao_sincronizada (TP_SOLICITACAO, DATA_SINCRONISMO)
#             VALUES (?, ?)
#         """,
#             novos_sincronizados,
#         )

#         conexao.commit()
#     else:
#         log_info(f"Nenhuma autorização pendente para {data_alvo.strftime('%Y-%m-%d')}.")

#     cursor.close()
#     conexao.close()


# # 5. Loop principal executando os 50 dias retroativos
# if __name__ == "__main__":
#     hoje = datetime.now().date()
#     total_dias = 50

#     for i in range(total_dias, 0, -1):
#         data_processamento = hoje - timedelta(days=i)
#         try:
#             dados = executa(data_processamento)
#             exportar_para_csv(dados, data_processamento)
#         except Exception as e:
#             log_error(
#                 f"Erro no processamento do dia {data_processamento}: {str(e)}"
#             )
