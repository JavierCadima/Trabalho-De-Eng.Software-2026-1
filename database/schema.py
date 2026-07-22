from database.connection import get_connection

def init_db():
    """Cria todas as tabelas necessárias se não existirem."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Produtos (Baterias)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            marca TEXT NOT NULL,
            categoria TEXT CHECK(categoria IN ('Carro', 'Moto', 'Caminhao_Onibus', 'Acessorio')),
            amperagem INT,
            preco_venda REAL NOT NULL,
            preco_com_troca REAL NOT NULL,
            estoque_atual INT DEFAULT 0
        );
        """)

        # Clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT UNIQUE,
            telefone TEXT
        );
        """)

        # Vendas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER REFERENCES clientes(id),
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            subtotal REAL NOT NULL,
            desconto REAL DEFAULT 0.0,
            total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL
        );
        """)

        # Itens da Venda (Controle de Série e Sucata)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL REFERENCES vendas(id) ON DELETE CASCADE,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            numero_serie TEXT NOT NULL,
            entregou_sucata BOOLEAN NOT NULL,
            meses_garantia INTEGER DEFAULT 18
        );
        """)

        # Sucatas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque_sucata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            quantidade INTEGER NOT NULL,
            categoria TEXT NOT NULL
        );
        """)
        conn.commit()