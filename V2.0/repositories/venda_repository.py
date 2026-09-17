from database.connection import conectar_bd
from utils.crypto import cifrar_texto, decifrar_texto

class VendaRepository:
    @staticmethod
    def salvar(venda):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vendas (bateria_id, cliente_cpf, numero_serie, data_venda, com_troca, valor_pago, forma_pagamento, garantia_ate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            venda.bateria_id, 
            cifrar_texto(venda.cliente_cpf), 
            cifrar_texto(venda.numero_serie), 
            cifrar_texto(venda.data_venda), 
            venda.com_troca, 
            venda.valor_pago, 
            cifrar_texto(venda.forma_pagamento), 
            cifrar_texto(venda.garantia_ate)
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def consultar_vendas(opcao, parametro=None):
        conn = conectar_bd()
        cursor = conn.cursor()
        query_base = '''
            SELECT v.id, b.marca, b.modelo, v.cliente_cpf, v.numero_serie, 
                   v.data_venda, v.valor_pago, v.forma_pagamento, v.com_troca
            FROM vendas v
            JOIN baterias b ON v.bateria_id = b.id
        '''
        if opcao == '1':
            cursor.execute(query_base + " ORDER BY v.id DESC")
        elif opcao == '2':
            parametro_cifrado = cifrar_texto(parametro)
            cursor.execute(query_base + " WHERE v.cliente_cpf = ? ORDER BY v.id DESC", (parametro_cifrado,))
        elif opcao == '3':
            parametro_cifrado = cifrar_texto(parametro)
            cursor.execute(query_base + " WHERE v.numero_serie = ? ORDER BY v.id DESC", (parametro_cifrado,))
            
        vendas = cursor.fetchall()
        conn.close()

        vendas_decifradas = []
        for v in vendas:
            # v: (id, marca, modelo, cpf, serie, data, valor, pgto, com_troca)
            v_dec = (
                v[0],
                decifrar_texto(v[1]),
                decifrar_texto(v[2]),
                decifrar_texto(v[3]),
                decifrar_texto(v[4]),
                decifrar_texto(v[5]),
                v[6],
                decifrar_texto(v[7]),
                v[8]
            )
            vendas_decifradas.append(v_dec)
        return vendas_decifradas

    @staticmethod
    def buscar_garantia(busca):
        conn = conectar_bd()
        cursor = conn.cursor()
        busca_cifrada = cifrar_texto(busca)
        cursor.execute('''
            SELECT v.id, b.marca, b.modelo, v.numero_serie, v.cliente_cpf, v.data_venda, v.garantia_ate, v.bateria_id
            FROM vendas v
            JOIN baterias b ON v.bateria_id = b.id
            WHERE v.cliente_cpf = ? OR v.numero_serie = ?
        ''', (busca_cifrada, busca_cifrada))
        vendas = cursor.fetchall()
        conn.close()

        vendas_decifradas = []
        for v in vendas:
            # v: (id, marca, modelo, serie, cpf, data, garantia_ate, bateria_id)
            v_dec = (
                v[0],
                decifrar_texto(v[1]),
                decifrar_texto(v[2]),
                decifrar_texto(v[3]),
                decifrar_texto(v[4]),
                decifrar_texto(v[5]),
                decifrar_texto(v[6]),
                v[7]
            )
            vendas_decifradas.append(v_dec)
        return vendas_decifradas

    @staticmethod
    def atualizar_numero_serie(venda_id, novo_numero_serie):
        conn = conectar_bd()
        cursor = conn.cursor()
        serie_cifrada = cifrar_texto(novo_numero_serie)
        cursor.execute("UPDATE vendas SET numero_serie = ? WHERE id = ?", (serie_cifrada, venda_id))
        conn.commit()
        conn.close()