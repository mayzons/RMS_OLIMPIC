import pandas as pd  # TYPE: IGNORE
from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_TRATAR
)
import os
import unicodedata
import re
from utils.logs_escrita import log_info, log_error


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


def opc():
    # Lista todos os arquivos do diretório
    arquivos_pasta = os.listdir(PASTA_TRATAR)
    total_arquivos = len(arquivos_pasta)
    arquivos_ok = []

    for arquivo in arquivos_pasta:
        if 'opc ' in arquivo.lower():
            arquivos_ok.append(arquivo)

    if total_arquivos > 0:
        for arquivo in arquivos_ok:
            if 'opc ' in arquivo.lower():
                caminho_arquivo = os.path.join(PASTA_TRATAR, arquivo)
                nome, extensao = os.path.splitext(arquivo)
            arquivo_saida = os.path.join(PASTA_DESTINO, arquivo)
            aba_especifica = "Page 1"

            try:
                log_info("Abrindo arquivo Excel de OPC...")

                df = pd.read_excel(
                    caminho_arquivo,
                    sheet_name=aba_especifica,
                    engine="openpyxl"
                )

                log_info("Arquivo OPC carregado com sucesso.")

                # Extrai a data do nome do arquivo (ex: "opc 01.08.2025.xlsx")
                data_report_str = nome.lower().replace("opc ", "").strip()
                data_report_str = data_report_str.replace(".", "/")

                df["data_report"] = converter_data_segura(
                    pd.Series([data_report_str]))[0]

                # Formato BR na saída
                df["data_report"] = df["data_report"].dt.strftime("%d/%m/%Y")

                log_info("Coluna data_report criada com sucesso.")

                df = normalizar_colunas(df)

                colunas_desejadas = [
                    "codigo", "nome", "vip", "versao_da_solucao", "suspenso",
                    "suspended_date", "rua", "cidade", "estado", "cep",
                    "opc", "data_opc", "cnpj", "bandeira", "rede",
                    "tipo_de_servico", "ip", "classificacao",
                    "longitude", "latitude", "quantidade_de_pistas",
                    "data_report"
                ]

                # print(df.columns.tolist())

                faltando = set(colunas_desejadas) - set(df.columns)

                if faltando:
                    raise Exception(f"Colunas não encontradas no arquivo: {faltando}")  # NOQA

                df = df[colunas_desejadas]

                # TRATAR COLUNA CODIGO
                df["codigo"] = df["codigo"].astype(str)

                # cria nova coluna removendo tudo após o traço
                df["codigo_tratado"] = df["codigo"].str.split("-").str[0].str.strip()  # NOQA

                # remove .0 caso venha de célula numérica do Excel
                df["codigo_tratado"] = df["codigo_tratado"].str.replace(
                    r"\.0$", "", regex=True)

                os.makedirs(PASTA_DESTINO, exist_ok=True)

                df.to_excel(
                    arquivo_saida,
                    index=False,
                    engine="openpyxl"
                )

                os.system(f'del "{caminho_arquivo}"')

                log_info(f"Arquivo Excel gerado com sucesso: {arquivo_saida}")
                return True

            except Exception as e:
                log_error("ERRO NA EXTRAÇÃO:")
                log_error(str(e))
                return False
        else:
            log_info("Nenhum arquivo de Critical encontrado para processar.")
