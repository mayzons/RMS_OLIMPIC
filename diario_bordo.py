import pandas as pd
from datetime import datetime, timedelta
from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_DIARIO,
    ARQUIVO_CONTROLE
)
import os
from utils.logs_escrita import log_info, log_error
import json


def diario():

    arquivo_saida = os.path.join(PASTA_DESTINO, "diario.csv")

    aba_especifica = "DIARIO"

    try:

        log_info("Abrindo arquivo Excel Diário...")

        df = pd.read_excel(
            PASTA_DIARIO,
            sheet_name=aba_especifica,
            engine="openpyxl"
        )

        log_info("Arquivo Diário carregado.")

        os.makedirs(PASTA_DESTINO, exist_ok=True)

        df.to_csv(
            arquivo_saida,
            index=False,
            sep=",",
            encoding="utf-8-sig"
        )

        log_info(f"Arquivo salvo em: {arquivo_saida}")
        return True

    except Exception as e:

        log_error("ERRO NA EXTRAÇÃO:")
        log_error(str(e))
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


def gatilho_diario():

    if not dentro_da_janela():
        log_info("Fora da janela (07-20). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_diario"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina Diário...")
        executar = True

        controle["proxima_execucao_diario"] = (
            agora + timedelta(hours=controle["horas_diario"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        try:
            diario()
            salvar_controle(controle)
            return True
        except Exception as e:
            log_error(f"Erro ao executar rotina Diário: {str(e)}")
            return False
    else:
        log_info("Ainda não chegou o horário da execução.")
