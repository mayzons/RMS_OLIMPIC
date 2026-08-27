import configparser
import sys
import os


# # Caminho do Parser
def get_app_and_settings_full_path():
    if getattr(sys, 'frozen', False):
        BASE_PATH = os.path.dirname(sys.executable)
    else:
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    
    # Sobe 1 nível no diretório (pasta raiz do projeto)
    ROOT_PATH = os.path.abspath(os.path.join(BASE_PATH, ".."))
    
    return BASE_PATH, os.path.join(BASE_PATH, "Config.ini"), ROOT_PATH

# Desempacotamento das 3 saídas
CAM_LOGS_LOGS, CAM_CONFIG_PARSER, CAM_ROOT_PROJECT = get_app_and_settings_full_path()



# Criar objeto do configparser
config = configparser.ConfigParser()
with open(CAM_CONFIG_PARSER, "r", encoding="utf-8") as file:
    config.read_file(file)

# Ler o arquivo ini
ambiente = config["ambiente"]["ambiente"]

# Acessar os valores das seções e chaves
PASTA_ROOT = CAM_ROOT_PROJECT
LOG_ESCRITA = config[ambiente]["log"]
CAMINHO_LOGS = config[ambiente]["caminho_logs"]
PASTA_DESTINO = config[ambiente]["cam_destino"]
PASTA_ANALISE = config[ambiente]['cam_analise']
PASTA_ZERO = config[ambiente]['cam_zero']
PASTA_COMPONENTES = config[ambiente]['cam_componentes']
PASTA_TRATAR = config[ambiente]['cam_tratar']
PASTABKP_DESTINO = config[ambiente]['cam_backup']
PASTA_TRN = config[ambiente]['cam_transacao']
PASTA_AUT = config[ambiente]['cam_autorizacoes']
CONSUMO_NATA = config[ambiente]['cam_consumo_nata']
PASTA_GRAFANA = config[ambiente]['cam_grafana']
ARQUIVO_CONTROLE = config[ambiente]['cam_json']
DIAS_FILTRO_ZERO = int(config[ambiente]['dias_filtro_zero'])
DIAS_FILTRO_ANALISE = int(config[ambiente]['dias_filtro_ana'])
DIAS_FILTRO_COMPONENTES = int(config[ambiente]['dias_filtro_comp'])
DIAS_FILTRO_AUDIT = int(config[ambiente]['dias_filtro_audit'])
PASTA_AUDITORIA = config[ambiente]['cam_auditoria']
PASTA_LOGS = CAM_LOGS_LOGS
USER = config[ambiente]['USER']
PASSWORD = config[ambiente]['PASSWORD']
DNS = config[ambiente]['DNS']
PORT = config[ambiente]['PORT']
SERVICE = config[ambiente]['SERVICE']
ORACLE_HOME = config[ambiente]['ORACLE_HOME']
PASTA_DIARIO = config[ambiente]['cam_diario']
BANCO_DADOS = config[ambiente]['banco_dados']
