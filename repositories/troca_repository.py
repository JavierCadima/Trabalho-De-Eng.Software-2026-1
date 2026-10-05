from database.connection import conectar_bd
from utils.crypto import cifrar_texto, decifrar_texto

class TrocaRepository:
    @staticmethod
    def salvar(troca):
        conn = conectar_bd()
        cursor = conn.cursor()
        serie_cifrada = cifrar_texto(troca.numero_serie_defeito)
        defeito_cifrado = cifrar_texto(troca.defeito_relatado)
        data_cifrada = cifrar_texto(troca.data_troca)

        cursor.execute('''
            INSERT INTO trocas_garantia (venda_id, bateria_id, numero_serie_defeito, defeito_relatado, data_troca)
            VALUES (?, ?, ?, ?, ?)
        ''', (troca.venda_id, troca.bateria_id, serie_cifrada, 
              defeito_cifrado, data_cifrada))
        conn.commit()
        conn.close()

    @staticmethod
    def obter_totais_ruins():
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(com_troca), 0) FROM vendas")
        carcacas_troca = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trocas_garantia")
        garantias_defeito = cursor.fetchone()[0]
        conn.close()

        return carcacas_troca, garantias_defeito

    @staticmethod
    def obter_dados_relatorio():
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_pago), 0), COALESCE(SUM(com_troca), 0) FROM vendas")
        res_vendas = cursor.fetchone()

        cursor.execute('''
            SELECT t.id, b.marca, b.modelo, t.numero_serie_defeito, t.defeito_relatado, t.data_troca, t.status
            FROM trocas_garantia t
            JOIN baterias b ON t.bateria_id = b.id
        ''')
        defeitos = cursor.fetchall()
        conn.close()

        defeitos_decifrados = []
        for d in defeitos:
            # d: (id, marca, modelo, num_serie_def, defeito_rel, data_troca, status)
            d_dec = (
                d[0],
                decifrar_texto(d[1]),
                decifrar_texto(d[2]),
                decifrar_texto(d[3]),
                decifrar_texto(d[4]),
                decifrar_texto(d[5]),
                d[6]
            )
            defeitos_decifrados.append(d_dec)

        return res_vendas, defeitos_decifrados