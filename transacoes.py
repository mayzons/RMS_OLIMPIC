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
    transacoes = []

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
        TB0008_CD_CONVENIADO,
        TB0153_CD_NSU,
        TB0153_ID_DISPOSITIVO,
        TO_CHAR(tb0153_dt_transacao, 'DD/MM/YYYY HH24:MI') AS DATA,
        tb0153_id_pistaanterior,
        tb0138_cd_produto,
        TB0153_CD_TOKEN,
        tb0153_cd_placadispositivo,
        tb0153_cd_placaocr,
        tb0153_cd_cupomfiscal,
        tb0153_vl_transacao
    FROM
        CADMO.tb0153_transacaoconveniado
    WHERE
        tb0153_dt_transacao >= TRUNC(SYSDATE - 20)
        AND tb0138_cd_produto = '1'
    """

    resultado.execute(sql)
    rows = resultado.fetchall()

    transacoes.clear()
    transacoes.extend(rows)

    resultado.close()
    conexao.close()

    log_info(f'O Select retornou {len(transacoes)} Transações!')

    return transacoes


def exportar_para_csv(result):
    transacoes = result
    transacoes_encontradas = []
    transacoes_nao_encontradas = []

    log_info('Iniciando o cruzamento e exportação das transações!')

    # 1. Garante que o diretório 'DATA' existe no servidor
    pasta_banco = os.path.dirname(BANCO_ROOT)
    os.makedirs(pasta_banco, exist_ok=True)

    conexao = sqlite3.connect(BANCO_ROOT)
    cursor = conexao.cursor()

    # 2. Cria a tabela ANTES de tentar buscar os registros (evita erro de tabela inexistente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacao_sincronizada (
            NSU TEXT PRIMARY KEY,
            DATA_SINCRONISMO TEXT
        )
    """)
    conexao.commit()

    # 3. Busca NSUs já sincronizados
    cursor.execute("SELECT NSU FROM transacao_sincronizada")
    sincronizado = {str(row[0]).strip() for row in cursor.fetchall()}

    # 4. Separa transações pendentes
    for t in transacoes:
        nsu_oracle = str(t[1]).strip() if t[1] is not None else ""
        if nsu_oracle in sincronizado:
            transacoes_encontradas.append(t)
        else:
            transacoes_nao_encontradas.append(t)

    log_info(f"Encontrados (já sincronizados): {len(transacoes_encontradas)}")
    log_info(f"Não encontrados (pendentes): {len(transacoes_nao_encontradas)}")

    # 5. Gera CSV de pendentes e atualiza o controle no SQLite
    if transacoes_nao_encontradas:
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        caminho_csv = os.path.join(PASTA_DESTINO, "trans_pendentes.csv")

        with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo_csv:
            writer = csv.writer(arquivo_csv, delimiter=",")
            writer.writerow(["POSTO", "NSU", "TAG", "DATA", "PISTA", "PRODUTO", "TOKEN", "PLACA_CAD", "PLACA_OCR", "CUPOM", "VALOR"])
            writer.writerows(transacoes_nao_encontradas)

        log_info(f'CSV gerado com sucesso em: {caminho_csv}')

        data_sincronismo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        novos_sincronizados = [
            (str(t[1]).strip(), data_sincronismo) 
            for t in transacoes_nao_encontradas 
            if t[1] is not None
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO transacao_sincronizada (NSU, DATA_SINCRONISMO)
            VALUES (?, ?)
        """, novos_sincronizados)

        conexao.commit()
        log_info(f'{len(novos_sincronizados)} novos NSUs gravados na tabela transacao_sincronizada!')
    else:
        log_info('Nenhuma transação pendente para exportar ou gravar.')

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


def transacoes_historico():

    if not dentro_da_janela():
        log_info("Fora da janela (05-22). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_trnhist"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina TRN Historico...")
        executar = True

        controle["proxima_execucao_trnhist"] = (
            agora + timedelta(hours=controle["horas_trnhist"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        try:
            transacoes = executa()
            exportar_para_csv(transacoes)
            salvar_controle(controle)
            return True

        except Exception as e:
            log_error(f"Erro ao executar rotina TRN Historico: {str(e)}")
            return False

    else:
        log_info("Ainda não chegou o horário da execução.")
