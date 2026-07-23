import sqlite3
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "mecanica_baterias.db"

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa com suporte a Foreign Keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row["nome"])
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn