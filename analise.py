import pandas as pd
from datetime import datetime, timedelta
from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_ANALISE,
    DIAS_FILTRO_ANALISE,
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


# Conversão INTELIGENTE de data
def converter_data_segura(serie):

    br = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    us = pd.to_datetime(serie, format="%m/%d/%Y", errors="coerce")

    # usa o formato que gerou menos NaT
    if br.notna().sum() >= us.notna().sum():
        return br
    else:
        return us


def analise():

    arquivo_saida = os.path.join(PASTA_DESTINO, "analise.csv")

    aba_especifica = "Análise 0 - 90.00%"
    coluna_data = "data_report"

    try:

        log_info("Abrindo arquivo Excel Analise...")

        df = pd.read_excel(
            PASTA_ANALISE,
            sheet_name=aba_especifica,
            engine="openpyxl"
        )

        log_info("Arquivo Analise carregado.")

        df = normalizar_colunas(df)

        colunas_desejadas = [
            "codigo", "nome", "data_report", "analise", "tratativas",
            "observacoes", "data_conclusao", "qtd_dias", "abono"
        ]

        faltando = set(colunas_desejadas) - set(df.columns)

        if faltando:
            raise Exception(f"Colunas não encontradas: {faltando}")

        df = df[colunas_desejadas]

        # CONVERSÃO BLINDADA
        df[coluna_data] = converter_data_segura(df[coluna_data])

        df = df.dropna(subset=[coluna_data])

        # TRATAR COLUNA CODIGO
        df["codigo"] = df["codigo"].astype(str)

        # cria nova coluna removendo tudo após o traço
        df["codigo_tratado"] = df["codigo"].str.split("-").str[0].str.strip()

        # remove .0 caso venha de célula numérica do Excel
        df["codigo_tratado"] = df["codigo_tratado"].str.replace(
            r"\.0$", "", regex=True)

        # trabalha só com DATE
        hoje = datetime.now().date()
        data_limite = hoje - timedelta(days=DIAS_FILTRO_ANALISE)

        log_info(f"Data limite usada no filtro: {data_limite}")

        df_filtrado = df[df[coluna_data].dt.date >= data_limite]  # TYPE: IGNORE # NOQA

        log_info(f"Linhas originais: {len(df)}")
        log_info(f"Linhas filtradas: {len(df_filtrado)}")

        if df_filtrado.empty:
            log_error(
                f"Nenhum dado encontrado nos últimos {DIAS_FILTRO_ANALISE} dias."  # TYPE: IGNORE # NOQA
            )
            return

        os.makedirs(PASTA_DESTINO, exist_ok=True)

        # FORMATO BR NA SAÍDA
        df_filtrado[coluna_data] = df_filtrado[coluna_data].dt.strftime("%d/%m/%Y")  # TYPE: IGNORE # NOQA

        df_filtrado.to_csv(
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


def gatilho_analise():

    if not dentro_da_janela():
        log_info("Fora da janela (07-20). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_analise"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina Analise...")
        executar = True

        controle["proxima_execucao_analise"] = (
            agora + timedelta(hours=controle["horas_zero"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        analise()
        salvar_controle(controle)
    else:
        log_info("Ainda não chegou o horário da execução.")
