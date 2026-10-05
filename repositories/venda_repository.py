from database.connection import conectar_bd
from utils.crypto import cifrar_texto, decifrar_texto

class VendaRepository:
    @staticmethod
    def salvar(venda):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vendas (bateria_id, cliente_cpf, numero_serie, data_venda, com_troca, valor_pago, forma_pagamento, garantia_ate, cliente_nome, cliente_endereco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            venda.bateria_id, 
            cifrar_texto(venda.cliente_cpf), 
            cifrar_texto(venda.numero_serie), 
            cifrar_texto(venda.data_venda), 
            venda.com_troca, 
            venda.valor_pago, 
            cifrar_texto(venda.forma_pagamento), 
            cifrar_texto(venda.garantia_ate),
            cifrar_texto(venda.cliente_nome),
            cifrar_texto(venda.cliente_endereco)
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def consultar_vendas(opcao, parametro=None):
        import re
        conn = conectar_bd()
        cursor = conn.cursor()
        query_base = '''
            SELECT v.id, b.marca, b.modelo, v.cliente_cpf, v.numero_serie, 
                   v.data_venda, v.valor_pago, v.forma_pagamento, v.com_troca,
                   v.cliente_nome, v.cliente_endereco
            FROM vendas v
            JOIN baterias b ON v.bateria_id = b.id
            ORDER BY v.id DESC
        '''
        cursor.execute(query_base)
        vendas = cursor.fetchall()
        conn.close()

        parametro_limpo = parametro.strip() if parametro else ""
        parametro_numerico = re.sub(r'\D', '', parametro_limpo) if parametro_limpo else ""

        vendas_decifradas = []
        for v in vendas:
            # v: (id, marca, modelo, cpf, serie, data, valor, pgto, com_troca, cliente_nome, cliente_endereco)
            cpf_dec = decifrar_texto(v[3])
            serie_dec = decifrar_texto(v[4])
            nome_cli_dec = decifrar_texto(v[9]) if len(v) > 9 and v[9] else ""
            end_cli_dec = decifrar_texto(v[10]) if len(v) > 10 and v[10] else ""

            if opcao == '2' and parametro_limpo:
                cpf_numerico = re.sub(r'\D', '', cpf_dec)
                if parametro_limpo.lower() != cpf_dec.lower() and (not parametro_numerico or parametro_numerico != cpf_numerico):
                    continue
            elif opcao == '3' and parametro_limpo:
                if parametro_limpo.lower() != serie_dec.lower():
                    continue

            v_dec = (
                v[0],
                decifrar_texto(v[1]),
                decifrar_texto(v[2]),
                cpf_dec,
                serie_dec,
                decifrar_texto(v[5]),
                v[6],
                decifrar_texto(v[7]),
                v[8],
                nome_cli_dec,
                end_cli_dec
            )
            vendas_decifradas.append(v_dec)
        return vendas_decifradas

    @staticmethod
    def buscar_garantia(busca):
        import re
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, b.marca, b.modelo, v.numero_serie, v.cliente_cpf, v.data_venda, v.garantia_ate, v.bateria_id
            FROM vendas v
            JOIN baterias b ON v.bateria_id = b.id
            ORDER BY v.id DESC
        ''')
        vendas = cursor.fetchall()
        conn.close()

        busca_limpa = busca.strip().lower()
        busca_numerica = re.sub(r'\D', '', busca_limpa)

        vendas_decifradas = []
        for v in vendas:
            # v: (id, marca, modelo, serie, cpf, data, garantia_ate, bateria_id)
            serie_dec = decifrar_texto(v[3])
            cpf_dec = decifrar_texto(v[4])
            cpf_numerico = re.sub(r'\D', '', cpf_dec)

            match_serie = (busca_limpa == serie_dec.lower())
            match_cpf = (busca_limpa == cpf_dec.lower()) or (busca_numerica and busca_numerica == cpf_numerico)

            if match_serie or match_cpf:
                v_dec = (
                    v[0],
                    decifrar_texto(v[1]),
                    decifrar_texto(v[2]),
                    serie_dec,
                    cpf_dec,
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