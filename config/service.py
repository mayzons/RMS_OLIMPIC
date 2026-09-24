from datetime import datetime
from .database import conectar


def _converter(valor, tipo):
    if valor is None:
        return None

    if tipo == "inteiro":
        return int(valor)
    if tipo == "booleano":
        return str(valor).lower() in ("1", "true", "sim", "s", "yes", "y")
    return valor


class ConfigService:
    def get(self, chave, ambiente="PROD", default=None):
        with conectar() as conn:
            row = conn.execute(
                """SELECT valor, tipo FROM configuracoes
                   WHERE ambiente = ? AND chave = ? AND ativo = 1""",
                (ambiente, chave)
            ).fetchone()

        if not row:
            return default

        return _converter(row["valor"], row["tipo"])

    def salvar(self, chave, valor, ambiente="PROD",
               tipo="texto", descricao=None):
        with conectar() as conn:
            conn.execute(
                """
                INSERT INTO configuracoes
                    (ambiente, chave, valor, tipo, descricao, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(ambiente, chave)
                DO UPDATE SET
                    valor = excluded.valor,
                    tipo = excluded.tipo,
                    descricao = excluded.descricao,
                    ativo = 1
                """,
                (ambiente, chave, str(valor) if valor is not None else None,
                 tipo, descricao)
            )

    def listar(self, ambiente="PROD"):
        with conectar() as conn:
            return conn.execute(
                """SELECT * FROM configuracoes
                   WHERE ambiente = ? ORDER BY chave""",
                (ambiente,)
            ).fetchall()

    def excluir(self, chave, ambiente="PROD"):
        with conectar() as conn:
            conn.execute(
                "DELETE FROM configuracoes WHERE ambiente = ? AND chave = ?",
                (ambiente, chave)
            )


class TarefaService:
    def listar(self, apenas_ativas=False):
        sql = "SELECT * FROM tarefas"
        params = ()
        if apenas_ativas:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY id"

        with conectar() as conn:
            return conn.execute(sql, params).fetchall()

    def listar_ativas(self):
        return self.listar(apenas_ativas=True)

    def obter(self, tarefa_id):
        with conectar() as conn:
            return conn.execute(
                "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
            ).fetchone()

    def salvar(self, dados, tarefa_id=None):
        campos = (
            dados["nome"], dados["hora_inicio"], dados["hora_fim"],
            int(dados["intervalo"]), dados["acao"], dados["origem"],
            dados["destino"], int(dados["sem_parada"]), int(dados["ativo"]),
            dados.get("ultima_execucao"), dados.get("proxima_execucao")
        )

        with conectar() as conn:
            if tarefa_id:
                conn.execute(
                    """
                    UPDATE tarefas SET
                        nome=?, hora_inicio=?, hora_fim=?, intervalo=?,
                        acao=?, origem=?, destino=?, sem_parada=?, ativo=?,
                        ultima_execucao=?, proxima_execucao=?
                    WHERE id=?
                    """,
                    (*campos, tarefa_id)
                )
                return tarefa_id

            cur = conn.execute(
                """
                INSERT INTO tarefas
                (nome, hora_inicio, hora_fim, intervalo, acao, origem,
                 destino, sem_parada, ativo, ultima_execucao, proxima_execucao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                campos
            )
            return cur.lastrowid

    def excluir(self, tarefa_id):
        with conectar() as conn:
            conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))

    def alternar(self, tarefa_id):
        with conectar() as conn:
            conn.execute(
                """UPDATE tarefas
                   SET ativo = CASE ativo WHEN 1 THEN 0 ELSE 1 END
                   WHERE id = ?""",
                (tarefa_id,)
            )

    def registrar_execucao(self, tarefa_id, status, mensagem="",
                           inicio=None, fim=None):
        inicio = inicio or datetime.now().isoformat(sep=" ", timespec="seconds")
        with conectar() as conn:
            conn.execute(
                """
                INSERT INTO execucoes
                (tarefa_id, inicio, fim, status, mensagem)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tarefa_id, inicio, fim, status, mensagem)
            )
            conn.execute(
                """UPDATE tarefas SET ultima_execucao = ?
                   WHERE id = ?""",
                (fim or inicio, tarefa_id)
            )

    def execucoes(self, limite=30):
        with conectar() as conn:
            return conn.execute(
                """
                SELECT e.*, t.nome
                FROM execucoes e
                JOIN tarefas t ON t.id = e.tarefa_id
                ORDER BY e.id DESC
                LIMIT ?
                """,
                (limite,)
            ).fetchall()
