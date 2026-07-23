from database.connection import get_connection

class ClienteRepository:
    def salvar(self, cliente_dict):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, cpf_cnpj, telefone, veiculo, endereco)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente_dict["nome"],
            cliente_dict["cpf_cnpj"],
            cliente_dict.get("telefone", ""),
            cliente_dict.get("veiculo", ""),
            cliente_dict.get("endereco", "")
        ))
        conn.commit()
        conn.close()

    def atualizar(self, cliente_dict):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nome=?, cpf_cnpj=?, telefone=?, veiculo=?, endereco=?
            WHERE id=?
        """, (
            cliente_dict["nome"],
            cliente_dict["cpf_cnpj"],
            cliente_dict.get("telefone", ""),
            cliente_dict.get("veiculo", ""),
            cliente_dict.get("endereco", ""),
            cliente_dict["id"]
        ))
        conn.commit()
        conn.close()

    def deletar(self, cliente_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        conn.commit()
        conn.close()

    def listar_todos(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf_cnpj, telefone, veiculo, endereco FROM clientes ORDER BY nome ASC")
        rows = cursor.fetchall()
        conn.close()

        clientes = []
        for r in rows:
            clientes.append({
                "id": r[0],
                "nome": r[1],
                "cpf_cnpj": r[2],
                "telefone": r[3],
                "veiculo": r[4],
                "endereco": r[5] if len(r) > 5 else ""
            })
        return clientes