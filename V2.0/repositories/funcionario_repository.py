from database.connection import conectar_bd
from models.funcionario import Funcionario
from models.cargo import Cargo
from utils.crypto import cifrar_texto, decifrar_texto

class FuncionarioRepository:
    @staticmethod
    def obter_todos(apenas_ativos=True):
        conn = conectar_bd()
        cursor = conn.cursor()
        query = """
            SELECT f.id, f.matricula, f.nome, f.cargo_id, f.ativo, c.nome, c.permissoes,
                   c.nivel, f.senha_hash, f.senha_salt
            FROM funcionarios f
            JOIN cargos c ON f.cargo_id = c.id
        """
        if apenas_ativos:
            query += " WHERE f.ativo = 1"
        query += " ORDER BY f.id ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        funcionarios = []
        for r in rows:
            f_id, mat_cif, nome_cif, c_id, ativo, c_nome, c_perms, c_nivel, senha_hash, senha_salt = r
            cargo = Cargo(id=c_id, nome=c_nome, permissoes=c_perms, nivel=c_nivel)
            mat_dec = decifrar_texto(mat_cif)
            nome_dec = decifrar_texto(nome_cif)
            funcionarios.append(Funcionario(id=f_id, matricula=mat_dec, nome=nome_dec,
                                            cargo=cargo, ativo=ativo,
                                            senha_hash=senha_hash, senha_salt=senha_salt))
        return funcionarios

    @staticmethod
    def buscar_por_matricula(matricula):
        mat_procurada = str(matricula).strip()
        todos = FuncionarioRepository.obter_todos(apenas_ativos=True)
        for f in todos:
            if f.matricula == mat_procurada:
                return f
        return None

    @staticmethod
    def salvar(funcionario: Funcionario):
        if not funcionario.matricula or not funcionario.nome.strip():
            raise ValueError("Matrícula e nome são obrigatórios.")
        if (not funcionario.cargo
                or funcionario.cargo.tem_permissao("cargos_gerenciar")):
            raise ValueError("O cargo do dono não pode ser atribuído a outro funcionário.")
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT matricula FROM funcionarios")
        if any(decifrar_texto(row[0]) == funcionario.matricula
               for row in cursor.fetchall()):
            conn.close()
            raise ValueError("Já existe um funcionário com essa matrícula.")
        mat_cif = cifrar_texto(funcionario.matricula)
        nome_cif = cifrar_texto(funcionario.nome)
        cursor.execute(
            "INSERT INTO funcionarios (matricula, nome, cargo_id, ativo) VALUES (?, ?, ?, ?)",
            (mat_cif, nome_cif, funcionario.cargo.id, funcionario.ativo)
        )
        funcionario.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return funcionario

    @staticmethod
    def atualizar_cargo(funcionario_id, novo_cargo_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT permissoes FROM cargos WHERE id = ?", (novo_cargo_id,))
        cargo = cursor.fetchone()
        if not cargo:
            conn.close()
            raise ValueError("O cargo informado não existe.")
        if Cargo("", cargo[0]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O cargo do dono não pode ser atribuído a outro funcionário.")
        cursor.execute("UPDATE funcionarios SET cargo_id = ? WHERE id = ?", (novo_cargo_id, funcionario_id))
        conn.commit()
        conn.close()

    @staticmethod
    def atualizar(funcionario_id, matricula, nome, cargo_id):
        matricula = str(matricula).strip()
        nome = str(nome).strip()
        if not matricula or not nome:
            raise ValueError("Matrícula e nome são obrigatórios.")
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT matricula FROM funcionarios WHERE id = ?", (funcionario_id,))
        atual = cursor.fetchone()
        if not atual:
            conn.close()
            raise ValueError("O funcionário selecionado não existe.")
        cursor.execute("SELECT matricula FROM funcionarios WHERE id != ?", (funcionario_id,))
        for (matricula_cifrada,) in cursor.fetchall():
            if decifrar_texto(matricula_cifrada) == matricula:
                conn.close()
                raise ValueError("Já existe um funcionário com essa matrícula.")
        cursor.execute("SELECT permissoes FROM cargos WHERE id = ?", (cargo_id,))
        cargo = cursor.fetchone()
        if not cargo:
            conn.close()
            raise ValueError("O cargo selecionado não existe.")
        if Cargo("", cargo[0]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O cargo do dono não pode ser atribuído a outro funcionário.")
        cursor.execute(
            "UPDATE funcionarios SET matricula = ?, nome = ?, cargo_id = ? WHERE id = ?",
            (cifrar_texto(matricula), cifrar_texto(nome), cargo_id, funcionario_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def desativar(funcionario_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT c.permissoes FROM funcionarios f
               JOIN cargos c ON c.id = f.cargo_id WHERE f.id = ?""",
            (funcionario_id,),
        )
        cargo = cursor.fetchone()
        if not cargo:
            conn.close()
            raise ValueError("O funcionário selecionado não existe.")
        if Cargo("", cargo[0]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O funcionário dono não pode ser excluído.")
        cursor.execute("UPDATE funcionarios SET ativo = 0 WHERE id = ?", (funcionario_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def reativar(funcionario_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT f.ativo, c.permissoes FROM funcionarios f
               JOIN cargos c ON c.id = f.cargo_id WHERE f.id = ?""",
            (funcionario_id,),
        )
        funcionario = cursor.fetchone()
        if not funcionario:
            conn.close()
            raise ValueError("O funcionário selecionado não existe.")
        if Cargo("", funcionario[1]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O status do dono não pode ser alterado.")
        if funcionario[0]:
            conn.close()
            raise ValueError("O funcionário já está ativo.")
        cursor.execute("UPDATE funcionarios SET ativo = 1 WHERE id = ?", (funcionario_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def definir_credencial(funcionario_id, senha_hash, senha_salt):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE funcionarios SET senha_hash = ?, senha_salt = ? WHERE id = ? AND ativo = 1",
            (senha_hash, senha_salt, funcionario_id),
        )
        if cursor.rowcount != 1:
            conn.close()
            raise ValueError("Não foi possível atualizar a senha desse funcionário.")
        conn.commit()
        conn.close()
