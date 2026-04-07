from package.abertos import abertos
from package.sla import sla
from package.encerrado import encerrados
from package.opc import opc
from package.analise import gatilho_analise
from package.zero import gatilho_zero
from package.componentes import gatilho_componentes
from package.critical import critical
from package.trn import gatilho_trn
from package.aut import gatilho_aut
from package.diario_bordo import gatilho_diario
from package.expurgos import expurgos
from package.consumo_nata import nata_execucao

from utils.logs_escrita import log_info


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

    log_info("Iniciando o processo TRN_AUT...")
    gatilho_trn()
    log_info("Finalizando o processo TRN_AUT...")

    log_info("Iniciando o processo TRN_AUT...")
    gatilho_aut()
    log_info("Finalizando o processo TRN_AUT...")

    log_info("Iniciando o processo Diário...")
    gatilho_diario()
    log_info("Finalizando o processo Diário...")

    log_info("Iniciando o processo Expurgos...")
    expurgos()
    log_info("Finalizando o processo Expurgos...")

    log_info("Iniciando o processo Nata...")
    nata_execucao()
    log_info("Finalizando o processo Nata...")

    log_info("Processo de execução dos módulos finalizado.")
