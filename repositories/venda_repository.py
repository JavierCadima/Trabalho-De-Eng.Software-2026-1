from database.connection import get_connection
from models.venda import VendaDTO

class VendaRepository:
    def registrar_venda_transacao(self, conn, venda: VendaDTO, subtotal: float, total: float) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vendas (cliente_id, subtotal, desconto, total, forma_pagamento)
            VALUES (?, ?, ?, ?, ?)
        """, (venda.cliente_id, subtotal, venda.desconto, total, venda.forma_pagamento))
        return cursor.lastrowid

    def registrar_item(self, conn, venda_id: int, item):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, numero_serie, entregou_sucata, meses_garantia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (venda_id, item.produto_id, item.quantidade, item.preco_aplicado, item.numero_serie, item.entregou_sucata, item.meses_garantia))

    def buscar_por_numero_serie(self, numero_serie: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT iv.*, v.data_venda, p.nome as produto_nome 
                FROM itens_venda iv
                JOIN vendas v ON v.id = iv.venda_id
                JOIN produtos p ON p.id = iv.produto_id
                WHERE iv.numero_serie = ?
            """, (numero_serie,))
            row = cursor.fetchone()
            return dict(row) if row else None