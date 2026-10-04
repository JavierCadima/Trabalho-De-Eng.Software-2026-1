import os
import sqlite3
import json

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

    # Novas tabelas para RBAC e Gestão de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cargos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            permissoes TEXT,
            nivel INTEGER NOT NULL DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE,
            nome TEXT,
            cargo_id INTEGER,
            ativo INTEGER DEFAULT 1,
            senha_hash TEXT,
            senha_salt TEXT,
            FOREIGN KEY (cargo_id) REFERENCES cargos(id)
        )
    ''')

    cursor.execute("PRAGMA table_info(cargos)")
    colunas_cargos = {coluna[1] for coluna in cursor.fetchall()}
    migrando_hierarquia = "nivel" not in colunas_cargos
    if "nivel" not in colunas_cargos:
        cursor.execute("ALTER TABLE cargos ADD COLUMN nivel INTEGER NOT NULL DEFAULT 1")

    cursor.execute("PRAGMA table_info(funcionarios)")
    colunas_funcionarios = {coluna[1] for coluna in cursor.fetchall()}
    if "senha_hash" not in colunas_funcionarios:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN senha_hash TEXT")
    if "senha_salt" not in colunas_funcionarios:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN senha_salt TEXT")

    if migrando_hierarquia:
        cursor.execute("SELECT id, nome, permissoes FROM cargos")
        for cargo_id, nome, permissoes in cursor.fetchall():
            try:
                permissoes_cargo = json.loads(permissoes or "[]")
            except (TypeError, json.JSONDecodeError):
                permissoes_cargo = []
            if "cargos_gerenciar" in permissoes_cargo or "tudo" in permissoes_cargo:
                novo_nivel = 1_000_000
            elif "fiscal" in nome.lower() or "gerente" in nome.lower():
                novo_nivel = 100
            elif "vendedor" in nome.lower():
                novo_nivel = 10
            else:
                novo_nivel = 1
            cursor.execute("UPDATE cargos SET nivel = ? WHERE id = ?", (novo_nivel, cargo_id))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT UNIQUE,
            nome TEXT,
            endereco TEXT,
            telefone TEXT
        )
    ''')

    # Garantir colunas adicionais de cliente na tabela de vendas
    cursor.execute("PRAGMA table_info(vendas)")
    colunas_vendas = [c[1] for c in cursor.fetchall()]
    if "cliente_nome" not in colunas_vendas:
        cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_nome TEXT")
    if "cliente_endereco" not in colunas_vendas:
        cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_endereco TEXT")

    # Seed inicial de Cargos e Administrador Principal
    _inicializar_cargos_e_funcionarios(cursor)
    cursor.execute("SELECT id, permissoes FROM cargos")
    for cargo_id, permissoes in cursor.fetchall():
        try:
            permissoes_cargo = json.loads(permissoes or "[]")
        except (TypeError, json.JSONDecodeError):
            permissoes_cargo = []
        if "cargos_gerenciar" in permissoes_cargo or "tudo" in permissoes_cargo:
            cursor.execute("UPDATE cargos SET nivel = 1000000 WHERE id = ?", (cargo_id,))

    conn.commit()
    return conn

def _inicializar_cargos_e_funcionarios(cursor):
    import json
    from utils.crypto import cifrar_texto

    cursor.execute("SELECT COUNT(*) FROM cargos")
    total_cargos = cursor.fetchone()[0]

    if total_cargos == 0:
        cargos_padrao = [
            (
                "Dono / Gerente Principal",
                json.dumps([
                    "venda_realizar", "venda_remover_item", "cliente_ver_dados",
                    "cliente_cadastrar", "estoque_consultar", "estoque_gerenciar",
                    "garantia_consultar", "garantia_troca", "relatorios_ver",
                    "area_gerente", "funcionarios_gerenciar", "cargos_gerenciar"
                ])
            ),
            (
                "Fiscal / Gerente",
                json.dumps([
                    "venda_realizar", "venda_remover_item", "cliente_ver_dados",
                    "cliente_cadastrar", "estoque_consultar", "estoque_gerenciar",
                    "garantia_consultar", "garantia_troca", "area_gerente",
                    "funcionarios_gerenciar", "relatorios_ver"
                ])
            ),
            (
                "Vendedor",
                json.dumps([
                    "venda_realizar", "cliente_cadastrar", "estoque_consultar",
                    "garantia_consultar"
                ])
            )
        ]
        cursor.executemany(
            "INSERT INTO cargos (nome, permissoes, nivel) VALUES (?, ?, ?)",
            [
                (cargos_padrao[0][0], cargos_padrao[0][1], 1_000_000),
                (cargos_padrao[1][0], cargos_padrao[1][1], 100),
                (cargos_padrao[2][0], cargos_padrao[2][1], 10),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    total_funcs = cursor.fetchone()[0]

    if total_funcs == 0:
        cursor.execute("SELECT id FROM cargos WHERE nome = 'Dono / Gerente Principal'")
        cargo_dono_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM cargos WHERE nome = 'Fiscal / Gerente'")
        cargo_fiscal_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM cargos WHERE nome = 'Vendedor'")
        cargo_vendedor_id = cursor.fetchone()[0]

        funcs_padrao = [
            (cifrar_texto("1001"), cifrar_texto("Administrador Principal"), cargo_dono_id),
            (cifrar_texto("2001"), cifrar_texto("Mariana Fiscal"), cargo_fiscal_id),
            (cifrar_texto("3001"), cifrar_texto("Lucas Vendedor"), cargo_vendedor_id)
        ]
        cursor.executemany("INSERT INTO funcionarios (matricula, nome, cargo_id) VALUES (?, ?, ?)", funcs_padrao)