import configparser
import sys
import os


# Caminho do Parser
def get_app_and_settings_full_path():
    if getattr(sys, 'frozen', False):
        BASE_PATH = os.path.dirname(sys.executable)
    else:
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    return BASE_PATH, os.path.join(BASE_PATH, "Config.ini")


CAM_LOGS_LOGS, CAM_CONFIG_PARSER = get_app_and_settings_full_path()


# Criar objeto do configparser
config = configparser.ConfigParser()
with open(CAM_CONFIG_PARSER, "r", encoding="utf-8") as file:
    config.read_file(file)

# Ler o arquivo ini
ambiente = config["ambiente"]["ambiente"]

# Acessar os valores das seções e chaves
LOG_ESCRITA = config[ambiente]["log"]
PASTA_DESTINO = config[ambiente]["cam_destino"]
PASTA_ANALISE = config[ambiente]['cam_analise']
PASTA_ZERO = config[ambiente]['cam_zero']
PASTA_COMPONENTES = config[ambiente]['cam_componentes']
PASTA_TRATAR = config[ambiente]['cam_tratar']
PASTABKP_DESTINO = config[ambiente]['cam_backup']
PASTA_TRN = config[ambiente]['cam_transacao']
PASTA_AUT = config[ambiente]['cam_autorizacoes']
CONSUMO_NATA = config[ambiente]['cam_consumo_nata']
ARQUIVO_CONTROLE = config[ambiente]['cam_json']
DIAS_FILTRO_ZERO = int(config[ambiente]['dias_filtro_zero'])
DIAS_FILTRO_ANALISE = int(config[ambiente]['dias_filtro_ana'])
DIAS_FILTRO_COMPONENTES = int(config[ambiente]['dias_filtro_comp'])
PASTA_LOGS = CAM_LOGS_LOGS
USER = config[ambiente]['USER']
PASSWORD = config[ambiente]['PASSWORD']
DNS = config[ambiente]['DNS']
PORT = config[ambiente]['PORT']
SERVICE = config[ambiente]['SERVICE']
ORACLE_HOME = config[ambiente]['ORACLE_HOME']
PASTA_DIARIO = config[ambiente]['cam_diario']
BANCO_DADOS = config[ambiente]['banco_dados']
