import json
import os
import shutil
from datetime import datetime
from utils.caminhos import (TAREFAS_JSON)
from utils.logs_escrita import log_info


def carregar_json(caminho_json):
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho_json, dados):
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def dentro_do_horario(hora_inicio_str, hora_fim_str, sem_parada_str):
    # Regra 1: Se sem_parada == 'sim' ou os horários forem iguais, ignora a validação de janela
    if (
        sem_parada_str.lower() == "sim"
        or hora_inicio_str == hora_fim_str
    ):
        return True

    agora = datetime.now().time()
    inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
    fim = datetime.strptime(hora_fim_str, "%H:%M").time()

    if inicio <= fim:
        return inicio <= agora <= fim
    else:
        # Trata janelas que viram a noite (ex: 22:00 até 06:00)
        return agora >= inicio or agora <= fim


def executar_acao(origem, destino, acao):
    try:
        if not os.path.exists(origem):
            log_info(f"[ERRO] Origem não encontrada: {origem}")
            return False

        # Garante que a pasta de destino exista
        pasta_destino = (
            destino if os.path.isdir(destino) else os.path.dirname(destino)
        )
        if pasta_destino and not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)

        if acao.lower() == "copiar":
            if os.path.isdir(origem):
                shutil.copytree(origem, destino, dirs_exist_ok=True)
            else:
                shutil.copy2(origem, destino)
            log_info(f"[COPIAR] Sucesso de '{origem}' para '{destino}'")

        elif acao.lower() == "mover":
            shutil.move(origem, destino)
            log_info(f"[MOVER] Sucesso de '{origem}' para '{destino}'")

        else:
            log_info(f"[ERRO] Ação inválida: {acao}")
            return False

        return True
    except Exception as e:
        log_info(f"[ERRO] Falha ao executar ação '{acao}' de '{origem}' para '{destino}': {e}")
        return False

def processar_tarefas():
    tarefas = carregar_json(TAREFAS_JSON)
    agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for tarefa in tarefas:
        acao = tarefa.get("acao")
        origem = tarefa.get("de")
        destino = tarefa.get("para")
        h_inicio = tarefa.get("hora_inicio")
        h_fim = tarefa.get("hora_fim")
        sem_parada = tarefa.get("sem_parada", "nao")

        # Valida janela de execução
        if dentro_do_horario(h_inicio, h_fim, sem_parada):
            log_info(f"Executando tarefa: {acao} de '{origem}' -> '{destino}'")
            sucesso = executar_acao(origem, destino, acao)

            if sucesso:
                # Atualiza o campo ultima_execucao no JSON
                tarefa["ultima_execucao"] = agora_str
        else:
            log_info(
                f"Fora do horário de execução ({h_inicio} - {h_fim}): {origem}"
            )

    # Grava a data/hora atualizada de volta no JSON
    salvar_json(TAREFAS_JSON, tarefas)
