# Exemplo de como sua aplicação existente pode
# consumir as configurações do banco.

from config.service import ConfigService, TarefaService

config = ConfigService()

PASTA_DESTINO = config.get("cam_destino")
PASTA_ANALISE = config.get("cam_analise")
PASTA_ZERO = config.get("cam_zero")
USER = config.get("USER")
PASSWORD = config.get("PASSWORD")
DNS = config.get("DNS")
PORT = config.get("PORT")
SERVICE = config.get("SERVICE")

print("PASTA_DESTINO:", PASTA_DESTINO)
print("PASTA_ANALISE:", PASTA_ANALISE)
print("PASTA_ZERO:", PASTA_ZERO)
print("DNS:", DNS)

tarefas = TarefaService().listar_ativas()

for tarefa in tarefas:
    print(
        tarefa["id"],
        tarefa["nome"],
        tarefa["origem"],
        tarefa["destino"],
        tarefa["intervalo"]
    )
