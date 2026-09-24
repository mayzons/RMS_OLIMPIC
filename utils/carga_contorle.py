import sqlite3
import os
from utils.caminhos import PASTA_ROOT

BANCO_ROOT = os.path.join(PASTA_ROOT, r"DATA\\banco_base.db")

# 1. Garante que o diretório 'DATA' existe no servidor
pasta_banco = os.path.dirname(BANCO_ROOT)
os.makedirs(pasta_banco, exist_ok=True)

conexao = sqlite3.connect(BANCO_ROOT)
cursor = conexao.cursor()

# 2. Cria a tabela ANTES de tentar buscar os registros (evita erro de tabela inexistente)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS autorizacao_sincronizada (
        TP_SOLICITACAO TEXT PRIMARY KEY,
        DATA_SINCRONISMO TEXT
    )
""")
conexao.commit()

# 3. Busca tokens já sincronizados
cursor.execute("SELECT TP_SOLICITACAO FROM autorizacao_sincronizada")
sincronizado = {str(row[0]).strip() for row in cursor.fetchall()}

# 4. Separa autorizações pendentes
for t in autorizacao:
    tp_solicitacao = str(t[7]).strip() if t[1] is not None else ""
    if tp_solicitacao in sincronizado:
        autorizacao_encontradas.append(t)
    else:
        autorizacao_nao_encontradas.append(t)

log_info(f"Encontradas (já sincronizadas): {len(autorizacao_encontradas)}")
log_info(f"Não encontradas (pendentes): {len(autorizacao_nao_encontradas)}")