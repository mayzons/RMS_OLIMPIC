from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "banco"
DB_PATH = DB_DIR / "configuracoes.db"


def conectar():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar():
    with conectar() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ambiente TEXT NOT NULL DEFAULT 'PROD',
            chave TEXT NOT NULL,
            valor TEXT,
            tipo TEXT NOT NULL DEFAULT 'texto',
            descricao TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            UNIQUE(ambiente, chave)
        );

        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            hora_inicio TEXT NOT NULL DEFAULT '05:00',
            hora_fim TEXT NOT NULL DEFAULT '22:00',
            intervalo INTEGER NOT NULL DEFAULT 60,
            acao TEXT NOT NULL DEFAULT 'copiar',
            origem TEXT,
            destino TEXT,
            sem_parada INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            ultima_execucao TEXT,
            proxima_execucao TEXT
        );

        CREATE TABLE IF NOT EXISTS execucoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarefa_id INTEGER NOT NULL,
            inicio TEXT NOT NULL,
            fim TEXT,
            status TEXT NOT NULL,
            mensagem TEXT,
            FOREIGN KEY(tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE
        );
        """)
