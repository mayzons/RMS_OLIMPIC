import pandas as pd
from datetime import datetime, timedelta
from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_COMPONENTES,
    DIAS_FILTRO_COMPONENTES,
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


def componentes():

    arquivo_saida = os.path.join(PASTA_DESTINO, "componentes.csv")

    aba_especifica = "Plan1"
    coluna_data = "data_considerar"

    try:

        log_info("Abrindo arquivo Excel Componentes...")

        df = pd.read_excel(
            PASTA_COMPONENTES,
            sheet_name=aba_especifica,
            engine="openpyxl"
        )

        log_info("Arquivo Componentes carregado.")

        df = normalizar_colunas(df)

        colunas_desejadas = [
            "componente",
            "data_considerar",
            "expurgo"
        ]

        faltando = set(colunas_desejadas) - set(df.columns)

        if faltando:
            raise Exception(f"Colunas não encontradas: {faltando}")

        df = df[colunas_desejadas]

        # ⭐ CONVERSÃO BLINDADA
        df[coluna_data] = converter_data_segura(df[coluna_data])

        df = df.dropna(subset=[coluna_data])

        # trabalha só com DATE
        hoje = datetime.now().date()
        data_limite = hoje - timedelta(days=DIAS_FILTRO_COMPONENTES)

        log_info(f"Data limite usada no filtro: {data_limite}")

        df_filtrado = df[df[coluna_data].dt.date >= data_limite]  # TYPE: IGNORE # NOQA

        log_info(f"Linhas originais: {len(df)}")
        log_info(f"Linhas filtradas: {len(df_filtrado)}")

        if df_filtrado.empty:
            log_error(
                f"Nenhum dado encontrado nos últimos {DIAS_FILTRO_COMPONENTES} dias."  # TYPE: IGNORE # NOQA
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


def gatilho_componentes():

    if not dentro_da_janela():
        log_info("Fora da janela (07-20). Encerrando execução.")
        return

    controle = carregar_controle()
    agora = datetime.now()

    executar = False

    proxima_execucao = datetime.strptime(
        controle["proxima_execucao_componentes"],
        "%Y-%m-%d %H:%M:%S"
    )

    if agora >= proxima_execucao:

        log_info("Executando rotina ZERO...")
        executar = True

        controle["proxima_execucao_componentes"] = (
            agora + timedelta(hours=controle["horas_componentes"])
        ).strftime("%Y-%m-%d %H:%M:%S")

    if executar:
        componentes()
        salvar_controle(controle)
    else:
        log_info("Ainda não chegou o horário da execução.")


if __name__ == "__main__":
    gatilho_componentes()
