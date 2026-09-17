import os
import sqlite3

def conectar_bd():
    """Conecta ao SQLite e garante a criação das tabelas necessárias."""
    conn = sqlite3.connect("loja_baterias.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baterias'")
    tabela_existe = cursor.fetchone()

    if not tabela_existe:
        if os.path.exists("banco.sql"):
            with open("banco.sql", "r", encoding="utf-8") as f:
                script_sql = f.read()
                conn.executescript(script_sql)
            print("\n[SISTEMA] Banco de dados criado e populado a partir de 'banco.sql'!")
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS baterias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT, modelo TEXT, amperagem INTEGER, cca INTEGER,
                    voltagem INTEGER, aplicacao TEXT, garantia_meses INTEGER,
                    quantidade INTEGER, preco_custo REAL, preco_venda REAL,
                    preco_minimo REAL, valor_carcaca REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bateria_id INTEGER, cliente_cpf TEXT, numero_serie TEXT,
                    data_venda TEXT, com_troca INTEGER, valor_pago REAL,
                    forma_pagamento TEXT, garantia_ate TEXT
                )
            ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trocas_garantia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            bateria_id INTEGER,
            numero_serie_defeito TEXT,
            defeito_relatado TEXT,
            data_troca TEXT,
            status TEXT DEFAULT 'Defeituosa (Aguardando Troca/Fábrica)',
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (bateria_id) REFERENCES baterias(id)
        )
    ''')

    conn.commit()
    return conn