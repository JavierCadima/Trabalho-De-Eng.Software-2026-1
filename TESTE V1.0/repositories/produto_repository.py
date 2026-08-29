from database.connection import get_connection

class ProdutoRepository:
    def salvar(self, produto_dict):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome, marca, categoria, amperagem, preco_venda, preco_com_troca, estoque_atual)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            produto_dict["nome"], produto_dict["marca"], produto_dict["categoria"],
            produto_dict["amperagem"], produto_dict["preco_venda"], produto_dict["preco_com_troca"],
            produto_dict["estoque_atual"]
        ))
        conn.commit()
        conn.close()

    def atualizar(self, produto_dict):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos 
            SET nome=?, marca=?, categoria=?, amperagem=?, preco_venda=?, preco_com_troca=?, estoque_atual=?
            WHERE id=?
        """, (
            produto_dict["nome"], produto_dict["marca"], produto_dict["categoria"],
            produto_dict["amperagem"], produto_dict["preco_venda"], produto_dict["preco_com_troca"],
            produto_dict["estoque_atual"], produto_dict["id"]
        ))
        conn.commit()
        conn.close()

    def deletar(self, produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conn.commit()
        conn.close()

    def buscar_por_id(self, produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, marca, categoria, amperagem, preco_venda, preco_com_troca, estoque_atual FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "nome": row[1],
                "marca": row[2],
                "categoria": row[3],
                "amperagem": row[4],
                "preco_venda": row[5],
                "preco_com_troca": row[6],
                "estoque_atual": row[7],
                "meses_garantia": 12
            }
        return None

    def listar_todos(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, marca, categoria, amperagem, preco_venda, preco_com_troca, estoque_atual FROM produtos ORDER BY nome ASC")
        rows = cursor.fetchall()
        conn.close()

        produtos = []
        for r in rows:
            produtos.append({
                "id": r[0], "nome": r[1], "marca": r[2], "categoria": r[3],
                "amperagem": r[4], "preco_venda": r[5], "preco_com_troca": r[6], "estoque_atual": r[7]
            })
        return produtos

    def dar_baixa_estoque(self, conn, produto_id, quantidade):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos 
            SET estoque_atual = estoque_atual - ? 
            WHERE id = ?
        """, (quantidade, produto_id))