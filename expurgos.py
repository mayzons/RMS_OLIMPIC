import pandas as pd  # type: ignore
from utils.caminhos import (
    PASTA_DESTINO, PASTA_TRATAR, PASTABKP_DESTINO
)
import os
import unicodedata
import re
from utils.logs_escrita import log_info, log_error
import datetime


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


def converter_data_segura(serie):
    br = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    us = pd.to_datetime(serie, format="%m/%d/%Y", errors="coerce")

    return br if br.notna().sum() >= us.notna().sum() else us


def expurgos():

    arquivos_pasta = os.listdir(PASTA_TRATAR)

    arquivos_ok = [
        a for a in arquivos_pasta
        if 'expurgos ' in a.lower() or 'abt hoje t' in a.lower()
    ]

    if not arquivos_ok:
        log_info("Nenhum arquivo Expurgos encontrado para processar.")
        return

    for arquivo in arquivos_ok:

        caminho_arquivo = os.path.join(PASTA_TRATAR, arquivo)
        nome, extensao = os.path.splitext(arquivo)
        arquivo_saida = os.path.join(PASTA_DESTINO, arquivo)

        try:

            if 'expurgos ' in arquivo.lower():
                log_info("Abrindo arquivo Excel de Expurgos...")

                data_report_str = nome.lower().replace(
                    "expurgos - ", "").strip()
                data_report_str = data_report_str.replace(".", "/")

                data_report = converter_data_segura(
                    pd.Series([data_report_str]))[0]

            elif 'abt hoje t' in arquivo.lower():
                log_info("Abrindo arquivo Excel de Abertos Hoje...")

                data_report = datetime.datetime.now()

            else:
                continue

            df = pd.read_excel(
                caminho_arquivo,
                sheet_name="Page 1",
                engine="openpyxl"
            )

            log_info("Arquivo carregado com sucesso.")

            # VERIFICA SE O ARQUIVO TEM DADOS
            if df.empty:
                log_info(f"Arquivo {arquivo} contém apenas cabeçalho. Será ignorado.")  # NOQA

                os.system(f'move "{caminho_arquivo}" "{PASTABKP_DESTINO}"')

                continue

            log_info("Arquivo carregado com sucesso.")

            df["data_report"] = data_report
            df["data_report"] = pd.to_datetime(
                df["data_report"]).dt.strftime("%d/%m/%Y")  # type: ignore

            df["arquivo_origem"] = arquivo

            log_info("Coluna data_report criada com sucesso.")

            df = normalizar_colunas(df)

            colunas_padrao = [
               "numero", "codigo", "empresa", "encerrado", "atualizado_por",
               "motivo_expurgo", "solicitado_expurgo",
               "status_solicitação_expurgo", "serviço_negocio",
               "atualizado_em", "data_report", "arquivo_origem"
            ]

            if len(df.columns) != len(colunas_padrao):
                raise ValueError(
                    f"Quantidade de colunas diferente do esperado. "
                    f"Esperado: {len(colunas_padrao)}, Encontrado: {len(df.columns)}"  # type: ignore # NOQA
                )

            df.columns = colunas_padrao

            # df["codigo_tratado"] = df["codigo"].str.split(
            #     "-").str[0].str.strip()

            # df["codigo_tratado"] = df["codigo_tratado"].str.replace(
            #     r"\.0$", "", regex=True
            # )
            df["codigo"] = df["codigo"].fillna("").astype(str)

            df["codigo_tratado"] = (
                df["codigo"]
                .str.replace(r"\.0$", "", regex=True)
                .str.split("-").str[0]
                .str.strip()
            )

            os.makedirs(PASTA_DESTINO, exist_ok=True)

            df.to_excel(
                arquivo_saida,
                index=False,
                engine="openpyxl"
            )

            os.system(f'move "{caminho_arquivo}" "{PASTABKP_DESTINO}"')

            log_info(f"Arquivo Excel gerado com sucesso: {arquivo_saida}")
            return True

        except Exception as e:
            log_error("ERRO NA EXTRAÇÃO:")
            log_error(str(e))
            return False