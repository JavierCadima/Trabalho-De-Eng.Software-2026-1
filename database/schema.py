from database.connection import get_connection

def _garantir_colunas(cursor, tabela, colunas_esperadas):
    """
    Verifica se a tabela possui todas as colunas necessárias.
    Adiciona automaticamente via ALTER TABLE as colunas que estiverem faltando.
    """
    cursor.execute(f"PRAGMA table_info({tabela});")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]
    
    if colunas_existentes:  # Se a tabela já existe
        for nome_coluna, tipo_coluna in colunas_esperadas.items():
            if nome_coluna not in colunas_existentes:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {nome_coluna} {tipo_coluna};")
                print(f"-> Migração: Coluna '{nome_coluna}' adicionada à tabela '{tabela}'.")


def _migrar_vendas_total_para_valor_total(cursor):
    cursor.execute("PRAGMA table_info(vendas);")
    colunas = {coluna[1] for coluna in cursor.fetchall()}
    if "total" not in colunas:
        return

    # Garante que valor_total exista antes de migrar dados
    if "valor_total" not in colunas:
        cursor.execute("ALTER TABLE vendas ADD COLUMN valor_total REAL NOT NULL DEFAULT 0.0;")
    cursor.execute("UPDATE vendas SET valor_total = total WHERE total IS NOT NULL;")

    def selecionar_coluna(nome, valor_padrao):
        return nome if nome in colunas else valor_padrao

    select_clause = [
        selecionar_coluna("id", "NULL"),
        selecionar_coluna("cliente_id", "NULL"),
        selecionar_coluna("data_venda", "CURRENT_TIMESTAMP"),
        selecionar_coluna("forma_pagamento", "'Dinheiro'"),
        selecionar_coluna("bandeira_cartao", "NULL"),
        selecionar_coluna("parcelas", "1"),
        selecionar_coluna("subtotal", "0.0"),
        selecionar_coluna("desconto", "0.0"),
        selecionar_coluna("valor_total", "0.0")
    ]

    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("ALTER TABLE vendas RENAME TO vendas_old;")
    cursor.execute("""
        CREATE TABLE vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            forma_pagamento TEXT NOT NULL,
            bandeira_cartao TEXT,
            parcelas INTEGER DEFAULT 1,
            subtotal REAL NOT NULL DEFAULT 0.0,
            desconto REAL DEFAULT 0.0,
            valor_total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        );
    """)
    cursor.execute(f"""
        INSERT INTO vendas (id, cliente_id, data_venda, forma_pagamento, bandeira_cartao, parcelas, subtotal, desconto, valor_total)
        SELECT {', '.join(select_clause)}
        FROM vendas_old;
    """)
    cursor.execute("DROP TABLE vendas_old;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    print("-> Migração: Coluna 'total' removida da tabela 'vendas' e dados migrados para 'valor_total'.")


def init_db():
    """
    Inicializa o esquema do banco de dados SQLite e garante que todas
    as tabelas e colunas necessárias existam.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT NOT NULL UNIQUE,
            telefone TEXT,
            veiculo TEXT,
            endereco TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    _garantir_colunas(cursor, "clientes", {
        "cpf_cnpj": "TEXT DEFAULT ''",
        "telefone": "TEXT DEFAULT ''",
        "veiculo": "TEXT DEFAULT ''",
        "endereco": "TEXT DEFAULT ''"
    })

    # 2. Tabela de Produtos / Catálogo de Baterias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            marca TEXT NOT NULL,
            categoria TEXT NOT NULL,
            amperagem INTEGER NOT NULL,
            preco_venda REAL NOT NULL,
            preco_com_troca REAL NOT NULL,
            estoque_atual INTEGER NOT NULL DEFAULT 0
        );
    """)

    # 3. Tabela Cabeçalho das Vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            forma_pagamento TEXT NOT NULL,
            bandeira_cartao TEXT,
            parcelas INTEGER DEFAULT 1,
            subtotal REAL NOT NULL DEFAULT 0.0,
            desconto REAL DEFAULT 0.0,
            valor_total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        );
    """)
    _garantir_colunas(cursor, "vendas", {
        "subtotal": "REAL NOT NULL DEFAULT 0.0",
        "valor_total": "REAL NOT NULL DEFAULT 0.0"
    })
    _migrar_vendas_total_para_valor_total(cursor)

    # 4. Tabela de Itens da Venda (Carrinho e Controle de Sucata)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_aplicado REAL NOT NULL,
            entregou_sucata BOOLEAN NOT NULL DEFAULT 1,
            numero_serie TEXT DEFAULT '',
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        );
    """)

    # 5. Tabela de Controle de Garantias (Número de Série)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS garantias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            numero_serie TEXT NOT NULL UNIQUE,
            data_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_validade DATETIME NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        );
    """)

    # 6. Tabela de Configurações da Loja (% Desconto CNPJ, etc)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    """)

    regras_padrao = [
        ('desconto_cnpj', '10.0'),
        ('desconto_cpf', '0.0'),
        ('desconto_pix', '5.0'),
        ('desconto_dinheiro', '5.0'),
        ('desconto_qtd_minima_percentual', '3.0'),
        ('desconto_qtd_minima_qtd', '3')
    ]
    for chave, valor in regras_padrao:
        cursor.execute(
            "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?);",
            (chave, valor)
        )

    conn.commit()
    conn.close()
    print("Banco de dados e tabelas (schema) verificados/inicializados com sucesso.")


if __name__ == "__main__":
    init_db()