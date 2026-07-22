import sqlite3
from pathlib import Path

DB_PATH = Path("mecanica_baterias.db")

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa com suporte a Foreign Keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row["nome"])
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn