from database.connection import get_connection
from models.venda import VendaDTO

class VendaRepository:
    def registrar_venda_transacao(self, conn, venda: VendaDTO, subtotal: float, total: float) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vendas (cliente_id, subtotal, desconto, valor_total, forma_pagamento)
            VALUES (?, ?, ?, ?, ?)
        """, (venda.cliente_id, subtotal, venda.desconto, total, venda.forma_pagamento))
        return cursor.lastrowid

    def registrar_item(self, conn, venda_id: int, item):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, numero_serie, entregou_sucata, meses_garantia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            venda_id,
            item.produto_id,
            item.quantidade,
            item.preco_aplicado,
            item.numero_serie or "",
            1 if item.entregou_sucata else 0,
            item.meses_garantia
        ))

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

    def listar_vendas_ultimos_3_meses(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                v.id, 
                v.data_venda, 
                COALESCE(c.nome, 'Cliente Avulso') AS cliente_nome,
                v.forma_pagamento, 
                v.desconto, 
                v.valor_total
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.data_venda >= DATE('now', '-3 month')
            ORDER BY v.data_venda DESC;
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def obter_ranking_baterias_mais_vendidas(self, limite=10):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.nome, 
                SUM(iv.quantidade) as total_vendido
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            JOIN vendas v ON iv.venda_id = v.id
            WHERE v.data_venda >= DATE('now', '-3 month')
            GROUP BY p.id, p.nome
            ORDER BY total_vendido DESC
            LIMIT ?;
        """, (limite,))
        rows = cursor.fetchall()
        conn.close()
        return rows
