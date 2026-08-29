import os
import sqlite3
import sys
from pathlib import Path

APP_NAME = "AutoMecanicaBaterias"

if getattr(sys, "frozen", False):
    DATA_DIR = Path(os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or Path.home() / "AppData" / "Local") / APP_NAME
else:
    DATA_DIR = Path(__file__).resolve().parent.parent

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "mecanica_baterias.db"

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa com suporte a Foreign Keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row["nome"])
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn