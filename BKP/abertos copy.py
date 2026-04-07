import pandas as pd
from utils.caminhos import (
    PASTA_DESTINO, PASTA_TRATAR, PASTABKP_DESTINO
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


def abertos():
    # Lista todos os arquivos do diretório
    arquivos_pasta = os.listdir(PASTA_TRATAR)
    total_arquivos = len(arquivos_pasta)
    arquivos_ok = []

    for arquivo in arquivos_pasta:
        if 'abertos ' in arquivo.lower():
            arquivos_ok.append(arquivo)

    if total_arquivos > 0:
        for arquivo in arquivos_ok:
            if 'abertos ' in arquivo.lower():
                caminho_arquivo = os.path.join(PASTA_TRATAR, arquivo)
                nome, extensao = os.path.splitext(arquivo)
            arquivo_saida = os.path.join(PASTA_DESTINO, arquivo)
            aba_especifica = "Page 1"

            try:
                log_info("Abrindo arquivo Excel de Abertos...")

                df = pd.read_excel(
                    caminho_arquivo,
                    sheet_name=aba_especifica,
                    engine="openpyxl"
                )

                log_info("Arquivo Abertos carregado com sucesso.")

                # Extrai a data do nome do arquivo (ex: "opc 01.08.2025.xlsx")
                data_report_str = nome.lower().replace(
                    "abertos - ", "").strip()
                data_report_str = data_report_str.replace(".", "/")

                df["data_report"] = converter_data_segura(
                    pd.Series([data_report_str]))[0]

                # Formato BR na saída
                df["data_report"] = df["data_report"].dt.strftime("%d/%m/%Y")

                df["arquivo_origem"] = arquivo

                log_info("Coluna data_report criada com sucesso.")

                df = normalizar_colunas(df)

                colunas_padrao = [
                    "numero", "tipo_tarefa", "type_wo", "estado",
                    "tipo_contato", "encerrado_por", "codigo", "empresa",
                    "modelo", "data_abertura", "data_encerramento", "subestado",  # NOQA
                    "descricao_resumida", "descricao", "grupo_designado",
                    "causa_erro", "close_code", "anotacoes_fechamento",
                    "vip", "versao_solucao", "integration_id",
                    "item_configuracao", "atribuido_a", "incidente_primario",
                    "data_inicio_real_trabalho", "data_termino_real_trabalho",
                    "id", "historico_ids", "contagem_reatribuicoes",
                    "atualizacoes", "servico_negocio", "estado_2", "cidade",
                    "rua", "quantidade_pistas", "rede", "data_atualizacao",
                    "atualizado_por", "opc", "tentativas_contato",
                    "aberto_por", "grupo_expedicao", "ibm", "tipo_operacao",
                    "data_envio_grupo", "data_report", "arquivo_origem"
                ]

                if len(df.columns) != len(colunas_padrao):
                    raise ValueError(
                        f"Quantidade de colunas diferente do esperado. "
                        f"Esperado: {len(
                            colunas_padrao)}, Encontrado: {len(df.columns)}"
                    )

                df.columns = colunas_padrao

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

                os.system(f'move "{caminho_arquivo}" "{PASTABKP_DESTINO}"')

                log_info(f"Arquivo Excel gerado com sucesso: {arquivo_saida}")

            except Exception as e:
                log_error("ERRO NA EXTRAÇÃO:")
                log_error(str(e))
        else:
            log_info("Nenhum arquivo Abertos encontrado para processar.")
