import re
from database.connection import conectar_bd
from models.cliente import Cliente
from utils.crypto import cifrar_texto, decifrar_texto

class ClienteRepository:
    @staticmethod
    def salvar(cliente: Cliente):
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cpf_cif = cifrar_texto(cliente.cpf)
        nome_cif = cifrar_texto(cliente.nome)
        end_cif = cifrar_texto(cliente.endereco)
        tel_cif = cifrar_texto(cliente.telefone)

        # Se já existir um cliente com esse CPF, atualiza os dados
        existente = ClienteRepository.buscar_por_cpf(cliente.cpf)
        if existente:
            cursor.execute("""
                UPDATE clientes 
                SET nome = ?, endereco = ?, telefone = ?
                WHERE id = ?
            """, (nome_cif, end_cif, tel_cif, existente.id))
            cliente.id = existente.id
        else:
            cursor.execute("""
                INSERT INTO clientes (cpf, nome, endereco, telefone)
                VALUES (?, ?, ?, ?)
            """, (cpf_cif, nome_cif, end_cif, tel_cif))
            cliente.id = cursor.lastrowid

        conn.commit()
        conn.close()
        return cliente

    @staticmethod
    def obter_todos():
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cpf, nome, endereco, telefone FROM clientes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        clientes = []
        for r in rows:
            c_id, cpf_c, nome_c, end_c, tel_c = r
            clientes.append(Cliente(
                id=c_id,
                cpf=decifrar_texto(cpf_c),
                nome=decifrar_texto(nome_c),
                endereco=decifrar_texto(end_c),
                telefone=decifrar_texto(tel_c)
            ))
        return clientes

    @staticmethod
    def buscar_por_cpf(cpf):
        cpf_busca = str(cpf).strip()
        cpf_num = re.sub(r'\D', '', cpf_busca)
        
        todos = ClienteRepository.obter_todos()
        for c in todos:
            c_num = re.sub(r'\D', '', c.cpf)
            if c.cpf.lower() == cpf_busca.lower() or (cpf_num and cpf_num == c_num):
                return c
        return None
