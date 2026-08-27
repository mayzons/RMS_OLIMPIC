import pandas as pd
from datetime import datetime, timedelta
from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_AUDITORIA,
    DIAS_FILTRO_AUDIT,
    ARQUIVO_CONTROLE
)
import os
import unicodedata
import re
from utils.logs_escrita import log_info, log_error
import json


def normalizar_colunas(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace('\xa0', ' ', regex=False)
        .str.lower()
    )

    df.columns = [
        unicodedata.normalize('NFKD', col)
        .encode('ascii', 'ignore')
        .decode('utf-8')
        for col in df.columns
    ]

    df.columns = [
        re.sub(r'[^a-z0-9]', '_', col)
        for col in df.columns
    ]

    df.columns = [
        re.sub(r'_+', '_', col).strip('_')
        for col in df.columns
    ]

    return df


# ⭐ Conversão INTELIGENTE de data
def converter_data_segura(serie):

    br = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    us = pd.to_datetime(serie, format="%m/%d/%Y", errors="coerce")

    # usa o formato que gerou menos NaT
    if br.notna().sum() >= us.notna().sum():
        return br
    else:
        return us


def audit():
    try:
        arquivo_saida = os.path.join(
            PASTA_DESTINO,
            "auditoria.xlsx"
        )

        aba_especifica = "Auditoria"

        # Lê mantendo nomes originais
        df_original = pd.read_excel(
            PASTA_AUDITORIA,
            sheet_name=aba_especifica,
            engine="openpyxl"
        )

        # Cria cópia para trabalhar
        df = df_original.copy()

        # Normaliza apenas para localizar colunas
        df = normalizar_colunas(df)

        coluna_data = "data_extracao"

        df[coluna_data] = converter_data_segura(df[coluna_data])

        df = df.dropna(subset=[coluna_data])

        hoje = datetime.now().date()
        data_limite = hoje - timedelta(days=DIAS_FILTRO_AUDIT)

        df_filtrado = df[df[coluna_data].dt.date >= data_limite]

        # Usa os índices filtrados para recuperar as linhas originais
        df_saida = df_original.loc[df_filtrado.index].copy()

        df_saida.to_excel(
            arquivo_saida,
            sheet_name="Auditoria",
            index=False,
            engine="openpyxl"
        )

        log_info(f"Arquivo XLSX salvo em: {arquivo_saida}")
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
    return 7 <= agora.hour < 23


def gatilho_audit():

    if not dentro_da_janela():
        log_info("Fora da janela (07-20). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_audit"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina AUDITORIA...")
        executar = True

        controle["proxima_execucao_audit"] = (
            agora + timedelta(hours=controle["horas_audit"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:

        try:
            audit()

            salvar_controle(controle)

            log_info(
                "Auditoria executada com sucesso."
            )

        except Exception as e:

            log_error(
                f"Falha na execução da auditoria: {e}"
            )
        else:
            log_info("Ainda não chegou o horário da execução.")
