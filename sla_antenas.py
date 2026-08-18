import os
import re
import unicodedata

import pandas as pd

from utils.caminhos import (
    PASTA_DESTINO,
    PASTA_TRATAR,
    PASTABKP_DESTINO
)
from utils.logs_escrita import log_info, log_error


def normalizar_colunas(df):
    df.columns = df.columns.map(str)

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
        .str.lower()
    )

    df.columns = [
        unicodedata.normalize("NFKD", col)
        .encode("ascii", "ignore")
        .decode("utf-8")
        for col in df.columns
    ]

    df.columns = [
        re.sub(r"[^a-z0-9]", "_", col)
        for col in df.columns
    ]

    df.columns = [
        re.sub(r"_+", "_", col).strip("_")
        for col in df.columns
    ]

    return df


def converter_data_segura(serie):
    br = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    us = pd.to_datetime(serie, format="%m/%d/%Y", errors="coerce")

    return br if br.notna().sum() >= us.notna().sum() else us


def antenas():

    arquivos = [
        arq for arq in os.listdir(PASTA_TRATAR)
        if "antenas " in arq.lower()
    ]

    if not arquivos:
        log_info("Nenhum arquivo de Antenas encontrado para processar.")
        return False

    for arquivo in arquivos:

        caminho_arquivo = os.path.join(PASTA_TRATAR, arquivo)
        arquivo_saida = os.path.join(PASTA_DESTINO, arquivo)

        nome, extensao = os.path.splitext(arquivo)

        try:

            log_info("Abrindo arquivo Excel de Antenas...")

            df = pd.read_excel(
                caminho_arquivo,
                sheet_name="Sheet1",
                engine="openpyxl",
                header=1
            )

            log_info("Arquivo carregado com sucesso.")

            # Remove a primeira linha após o cabeçalho
            df = df.drop(index=0).reset_index(drop=True)

            # Normaliza os nomes das colunas
            df = normalizar_colunas(df)

            print(df.columns.tolist())

            # Extrai o número da pista/IP
            if "nome" in df.columns:
                df["ip_pista"] = (
                    df["nome"]
                    .astype(str)
                    .str.extract(r"192\.168\.212\.(\d+)", expand=False)
                )
            else:
                df["ip_pista"] = None

            # Data do relatório a partir do nome do arquivo
            data_report_str = (
                nome.lower()
                .replace("antenas - ", "")
                .strip()
                .replace(".", "/")
            )

            data_report = converter_data_segura(
                pd.Series([data_report_str])
            )[0]

            df["data_report"] = data_report.strftime("%d/%m/%Y")
            df["arquivo_origem"] = arquivo

            log_info("Colunas data_report e arquivo_origem criadas.")

            colunas_desejadas = [
                "codigo",
                "nome",
                "modelo",
                "tempo_operacional",
                "tempo_indisponivel",
                "tempo_nao_operacional",
                "sla",
                "ip_pista",
                "data_report",
                "arquivo_origem"
            ]

            faltando = set(colunas_desejadas) - set(df.columns)

            if faltando:
                raise Exception(
                    f"Colunas não encontradas no arquivo: {sorted(faltando)}"
                )

            df = df[colunas_desejadas]

            os.makedirs(PASTA_DESTINO, exist_ok=True)

            df.to_excel(
                arquivo_saida,
                index=False,
                engine="openpyxl"
            )

            os.system(f'move "{caminho_arquivo}" "{PASTABKP_DESTINO}"')

            log_info(f"Arquivo gerado com sucesso: {arquivo_saida}")

        except Exception as e:
            log_error("ERRO NA EXTRAÇÃO:")
            log_error(str(e))
            return False

    return True