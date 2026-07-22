from typing import Optional, List
from database.connection import get_connection
from models.produto import Produto

class ProdutoRepository:
    def salvar(self, prod: Produto) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (nome, marca, categoria, amperagem, preco_venda, preco_com_troca, estoque_atual)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (prod.nome, prod.marca, prod.categoria, prod.amperagem, prod.preco_venda, prod.preco_com_troca, prod.estoque_atual))
            return cursor.lastrowid

    def buscar_por_id(self, produto_id: int) -> Optional[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def dar_baixa_estoque(self, conn, produto_id: int, qtd: int):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?
        """, (qtd, produto_id))