import configparser
import json
from pathlib import Path

from .database import inicializar
from .service import ConfigService, TarefaService


def encontrar_arquivo(nome, raiz):
    candidatos = [
        raiz / nome,
        raiz / "config" / nome,
        raiz.parent / nome,
    ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None


def importar_ini(caminho):
    if not caminho or not caminho.exists():
        return 0

    parser = configparser.ConfigParser()
    parser.read(caminho, encoding="utf-8")

    service = ConfigService()
    ambiente_atual = parser.get("ambiente", "ambiente", fallback="PROD")

    total = 0
    for secao in parser.sections():
        if secao.lower() == "ambiente":
            continue

        for chave, valor in parser.items(secao):
            tipo = "inteiro" if chave.startswith("dias_filtro_") else "texto"
            service.salvar(
                chave=chave,
                valor=valor,
                ambiente=secao,
                tipo=tipo,
                descricao=f"Importado do Config.ini (ambiente atual: {ambiente_atual})"
            )
            total += 1

    return total


def importar_tarefas(caminho):
    if not caminho or not caminho.exists():
        return 0

    with caminho.open("r", encoding="utf-8") as f:
        dados = json.load(f)

    if isinstance(dados, dict):
        dados = dados.get("tarefas", [])

    service = TarefaService()
    total = 0

    for i, item in enumerate(dados, start=1):
        dados_tarefa = {
            "nome": item.get("nome", f"Tarefa importada {i}"),
            "hora_inicio": item.get("hora_inicio", "05:00"),
            "hora_fim": item.get("hora_fim", "22:00"),
            "intervalo": item.get("intervalo", 60),
            "acao": item.get("acao", "copiar"),
            "origem": item.get("de", ""),
            "destino": item.get("para", ""),
            "sem_parada": str(item.get("sem_parada", "nao")).lower()
                           in ("sim", "s", "1", "true"),
            "ativo": 1,
            "ultima_execucao": item.get("ultima_execucao"),
            "proxima_execucao": None,
        }
        service.salvar(dados_tarefa)
        total += 1

    return total


def importar_controle(caminho):
    # O controle atual usa chaves específicas por rotina.
    # Nesta primeira estrutura, preservamos os dados como configurações.
    if not caminho or not caminho.exists():
        return 0

    with caminho.open("r", encoding="utf-8") as f:
        dados = json.load(f)

    service = ConfigService()
    total = 0

    for chave, valor in dados.items():
        tipo = "inteiro" if isinstance(valor, int) else "texto"
        service.salvar(
            chave=f"controle.{chave}",
            valor=valor,
            ambiente="CONTROLE",
            tipo=tipo,
            descricao="Importado de controle_execucao.json"
        )
        total += 1

    return total


def executar_migracao(raiz=None):
    raiz = Path(raiz or Path.cwd())
    inicializar()

    ini = encontrar_arquivo("Config.ini", raiz)
    tarefas = encontrar_arquivo("tarefas.json", raiz)
    controle = encontrar_arquivo("controle_execucao.json", raiz)

    return {
        "config_ini": importar_ini(ini),
        "tarefas": importar_tarefas(tarefas),
        "controle": importar_controle(controle),
    }
