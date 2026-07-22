class SucataRepository:
    def incrementar_sucata(self, conn, quantidade: int, categoria: str):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO estoque_sucata (quantidade, categoria) VALUES (?, ?)
        """, (quantidade, categoria))