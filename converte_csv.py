import os
import pandas as pd
from utils.caminhos import PASTA_DESTINO, PASTA_CSV
from utils.logs_escrita import log_info, log_error


def gera_csv():

    os.makedirs(PASTA_DESTINO, exist_ok=True)

    contador = 0

    for arquivo in os.listdir(PASTA_CSV):

        # Processar apenas arquivos Excel
        if not arquivo.lower().endswith((".xlsx", ".xls")):
            continue

        caminho_arquivo = os.path.join(PASTA_CSV, arquivo)
        nome, _ = os.path.splitext(arquivo)
        caminho_saida = os.path.join(PASTA_DESTINO, f"{nome}.csv")

        try:
            log_info(f"Iniciando conversão do arquivo: {arquivo}")

            # Lê primeira aba
            df = pd.read_excel(
                caminho_arquivo,
                sheet_name=0,
                dtype=str,
                engine="openpyxl"
            )

            # Converte direto para CSV (forma correta)
            df.to_csv(
                caminho_saida,
                index=False,
                encoding="utf-8"
            )

            # Remove arquivo original após sucesso
            os.remove(caminho_arquivo)

            contador += 1

            log_info(f"CSV gerado com sucesso em: {caminho_saida}")
            log_info(f"Arquivo original removido: {arquivo}")
            return True

        except Exception as e:
            log_error(f"Erro ao converter {arquivo}")
            log_error(str(e))
            return False

    log_info(f"\n🎯 {contador} arquivos convertidos para CSV com sucesso!")
