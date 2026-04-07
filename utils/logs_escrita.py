from datetime import datetime
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.caminhos import PASTA_LOGS, LOG_ESCRITA


# Variaveis
hora_atual = datetime.now()
nm_log_data = datetime.strftime(datetime.now(), '%Y-%m-%d')
CAMINHO_LOGS = PASTA_LOGS
nome_log = f'{nm_log_data}'

raiz_pasta = r'C:\\script\\processos\\logs'

os.makedirs(raiz_pasta, exist_ok=True)
# TEMP
CAMINHO_LOGS = raiz_pasta

logger = logging.getLogger()
cwd = os.getcwd()
handler = TimedRotatingFileHandler(
    f'{CAMINHO_LOGS}\\{nm_log_data}.log',
    when='midnight', interval=1, backupCount=15)
handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def log_warning(message):
    if LOG_ESCRITA == 'Sim':
        logger.warning(message)


def log_info(message):
    if LOG_ESCRITA == 'Sim':
        logger.info(message)


def log_debug(message):
    if LOG_ESCRITA == 'Sim':
        logger.debug(message)


def log_critical(message):
    if LOG_ESCRITA == 'Sim':
        logger.info(message)


def log_error(message):
    if LOG_ESCRITA == 'Sim':
        logger.info(message)
