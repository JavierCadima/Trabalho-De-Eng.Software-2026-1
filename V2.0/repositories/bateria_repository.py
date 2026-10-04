from database.connection import conectar_bd
from utils.crypto import cifrar_texto, decifrar_texto

class BateriaRepository:
    @staticmethod
    def buscar_baterias(termo):
        conn = conectar_bd()
        cursor = conn.cursor()
        termo = termo.strip()
        if termo.isdigit():
            cursor.execute("""
                SELECT id, marca, modelo, amperagem, cca, quantidade, preco_venda, preco_minimo, valor_carcaca, garantia_meses 
                FROM baterias WHERE id = ?
            """, (int(termo),))
            resultados = cursor.fetchall()
            conn.close()
            baterias_decifradas = []
            for b in resultados:
                b_dec = (b[0], decifrar_texto(b[1]), decifrar_texto(b[2]), b[3], b[4], b[5], b[6], b[7], b[8], b[9])
                baterias_decifradas.append(b_dec)
            return baterias_decifradas
        else:
            cursor.execute("""
                SELECT id, marca, modelo, amperagem, cca, quantidade, preco_venda, preco_minimo, valor_carcaca, garantia_meses 
                FROM baterias
            """)
            todos = cursor.fetchall()
            conn.close()
            termo_lower = termo.lower()
            baterias_decifradas = []
            for b in todos:
                marca_dec = decifrar_texto(b[1])
                modelo_dec = decifrar_texto(b[2])
                nome_completo = f"{marca_dec} {modelo_dec}".lower()
                if (termo_lower in marca_dec.lower()) or (termo_lower in modelo_dec.lower()) or (termo_lower in nome_completo):
                    b_dec = (b[0], marca_dec, modelo_dec, b[3], b[4], b[5], b[6], b[7], b[8], b[9])
                    baterias_decifradas.append(b_dec)
            return baterias_decifradas

    @staticmethod
    def salvar(bateria):
        conn = conectar_bd()
        cursor = conn.cursor()
        marca_cifrada = cifrar_texto(bateria.marca)
        modelo_cifrado = cifrar_texto(bateria.modelo)
        aplicacao_cifrada = cifrar_texto(bateria.aplicacao)

        cursor.execute('''
            INSERT INTO baterias 
            (marca, modelo, amperagem, cca, voltagem, aplicacao, garantia_meses, quantidade, preco_custo, preco_venda, preco_minimo, valor_carcaca)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (marca_cifrada, modelo_cifrado, bateria.amperagem, bateria.cca, bateria.voltagem, 
              aplicacao_cifrada, bateria.garantia_meses, bateria.quantidade, bateria.preco_custo, 
              bateria.preco_venda, bateria.preco_minimo, bateria.valor_carcaca))
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar_estoque(bateria_id, quantidade_add):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("UPDATE baterias SET quantidade = quantidade + ? WHERE id = ?", (quantidade_add, bateria_id))
        conn.commit()
        conn.close()

    @staticmethod
    def decrementar_estoque(bateria_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("UPDATE baterias SET quantidade = quantidade - 1 WHERE id = ?", (bateria_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def obter_todas():
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, marca, modelo, amperagem, cca, aplicacao, quantidade, preco_venda, preco_minimo, valor_carcaca FROM baterias")
        baterias = cursor.fetchall()
        conn.close()

        baterias_decifradas = []
        for b in baterias:
            b_dec = (b[0], decifrar_texto(b[1]), decifrar_texto(b[2]), b[3], b[4], decifrar_texto(b[5]), b[6], b[7], b[8], b[9])
            baterias_decifradas.append(b_dec)
        return baterias_decifradas

    @staticmethod
    def atualizar_precos(bateria_id, novo_venda, novo_minimo, novo_carcaca):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE baterias 
            SET preco_venda = ?, preco_minimo = ?, valor_carcaca = ?
            WHERE id = ?
        ''', (novo_venda, novo_minimo, novo_carcaca, bateria_id))
        conn.commit()
        conn.close()

    @staticmethod
    def obter_quantidade_estoque(bateria_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM baterias WHERE id = ?", (bateria_id,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else 0