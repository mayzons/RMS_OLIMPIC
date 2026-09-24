from abertos import abertos
from sla import sla
from encerrado import encerrados
from opc import opc
from analise import gatilho_analise
from zero import gatilho_zero
from componentes import gatilho_componentes
from critical import critical
from ultima_transacao_posto import gatilho_trn
from autorizacoes import gatilho_aut
from diario_bordo import gatilho_diario
from expurgos import expurgos
from consumo_nata import nata_execucao
from ultima_transacao_pistas import gatilho_trn_pista
from auditoria import gatilho_audit
from sla_antenas import antenas
from grafana import grafana
from detalhado import detalhado
from transacoes import transacoes_historico
from autorizacao import autorizacao_historico
from move_copy import processar_tarefas
from atualiza_disp import gat_manual
from workservicos import gat_servicos

from utils.logs_escrita import log_info
from utils.caminhos import ORACLE_HOME
import oracledb

oracledb.init_oracle_client(
    lib_dir=ORACLE_HOME
)

if __name__ == "__main__":
    log_info("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    log_info("---------------------------- NOVA ROTINA - VERSAO 5, 3, 0, 0 ----------------------------")
    log_info("Iniciando o processo de execução dos módulos...")

    log_info("||||||||||||||||||||COPIA E MOVIMENTAÇÃO||||||||||||||||||||")

    log_info("Iniciando o processo Copia e Movimentação...")
    processar_tarefas()
    log_info("||||||||||||||||||||TRANSACOES||||||||||||||||||||")
    
    log_info("Iniciando o processo TRN_AUT...")
    gatilho_trn()

    log_info("Iniciando o processo TRN_Pista...")
    gatilho_trn_pista()
    
    log_info("Iniciando o processo TRN Historico...")
    transacoes_historico()

    log_info("Iniciando o processo Autorização Historico...")
    autorizacao_historico()
    
    log_info("Iniciando o processo TRN_AUT...")
    gatilho_aut()

    log_info("||||||||||||||||||||CARGAS DATABRICKS||||||||||||||||||||")

    log_info("Iniciando o processo Abertos...")
    abertos()

    log_info("Iniciando o processo SLA...")
    sla()

    log_info("Iniciando o processo Encerrados...")
    encerrados()

    log_info("Iniciando o processo OPC...")
    opc()

    log_info("Iniciando o processo Grafana...")
    grafana()

    log_info("Iniciando o processo Análise...")
    gatilho_analise()

    log_info("Iniciando o processo Zero...")
    gatilho_zero()

    log_info("Iniciando o processo Componentes...")
    gatilho_componentes()

    log_info("Iniciando o processo Critical...")
    critical()

    log_info("Iniciando o processo Detalhado...")
    detalhado()

    log_info("Iniciando o processo Antenas...")
    antenas()

    log_info("Iniciando o processo Diário...")
    gatilho_diario()
   
    log_info("Iniciando o processo Expurgos...")
    expurgos()

    log_info("Iniciando o processo Auditoria...")
    gatilho_audit()
    
    log_info("||||||||||||||||||||ATUALIZAÇÕES||||||||||||||||||||")

    log_info("Iniciando o processo Atualização AUT DISP...")
    gat_manual()

    log_info("Iniciando o processo Atualização AUT ZERO...")
    gat_servicos()

    # log_info("             AÇÕES NATANAEL             ")

    # log_info("Iniciando o processo Nata...")
    # nata_execucao()

    log_info("Processo de execução dos módulos finalizado.")
