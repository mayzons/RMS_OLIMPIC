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

from utils.logs_escrita import log_info
from utils.caminhos import ORACLE_HOME
import oracledb

oracledb.init_oracle_client(
    lib_dir=ORACLE_HOME
)

if __name__ == "__main__":

    log_info("Iniciando o processo de execução dos módulos...")

    log_info("Iniciando o processo Abertos...")
    abertos()
    log_info("Finalizando o processo Abertos...")

    log_info("Iniciando o processo SLA...")
    sla()
    log_info("Finalizando o processo SLA...")

    log_info("Iniciando o processo Encerrados...")
    encerrados()
    log_info("Finalizando o processo Encerrados...")

    log_info("Iniciando o processo OPC...")
    opc()
    log_info("Finalizando o processo OPC...")

    log_info("Iniciando o processo Grafana...")
    grafana()
    log_info("Finalizando o processo Grafana...")

    log_info("Iniciando o processo Análise...")
    gatilho_analise()
    log_info("Finalizando o processo Análise...")

    log_info("Iniciando o processo Zero...")
    gatilho_zero()
    log_info("Finalizando o processo Zero...")

    log_info("Iniciando o processo Componentes...")
    gatilho_componentes()
    log_info("Finalizando o processo Componentes...")

    log_info("Iniciando o processo Critical...")
    critical()
    log_info("Finalizando o processo Critical...")

    log_info("Iniciando o processo Detalhado...")
    detalhado()
    log_info("Finalizando o processo Detalhado...")

    log_info("Iniciando o processo Antenas...")
    antenas()
    log_info("Finalizando o processo Antenas...")

    log_info("Iniciando o processo TRN_AUT...")
    gatilho_trn()
    log_info("Finalizando o processo TRN_AUT...")

    log_info("Iniciando o processo TRN_Pista...")
    gatilho_trn_pista()
    log_info("Finalizando o processo TRN_Pista...")
    
    log_info("Iniciando o processo TRN Historico...")
    transacoes_historico()
    log_info("Finalizando o processo TRN Historico...")

    log_info("Iniciando o processo TRN_AUT...")
    gatilho_aut()
    log_info("Finalizando o processo TRN_AUT...")

    log_info("Iniciando o processo Diário...")
    gatilho_diario()
    log_info("Finalizando o processo Diário...")

    log_info("Iniciando o processo Expurgos...")
    expurgos()
    log_info("Finalizando o processo Expurgos...")

    log_info("Iniciando o processo Auditoria...")
    gatilho_audit()
    log_info("Finalizando o processo Auditoria...")

    log_info("Iniciando o processo Nata...")
    nata_execucao()
    log_info("Finalizando o processo Nata...")

    log_info("Processo de execução dos módulos finalizado.")
