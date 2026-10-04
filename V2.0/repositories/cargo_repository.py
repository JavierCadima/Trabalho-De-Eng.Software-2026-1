import json
from database.connection import conectar_bd
from models.cargo import Cargo

class CargoRepository:
    @staticmethod
    def obter_todos():
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, permissoes, nivel FROM cargos ORDER BY nivel DESC, id ASC")
        rows = cursor.fetchall()
        conn.close()

        cargos = []
        for r in rows:
            cargos.append(Cargo(id=r[0], nome=r[1], permissoes=r[2], nivel=r[3]))
        return cargos

    @staticmethod
    def buscar_por_id(cargo_id):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, permissoes, nivel FROM cargos WHERE id = ?", (cargo_id,))
        r = cursor.fetchone()
        conn.close()
        if r:
            return Cargo(id=r[0], nome=r[1], permissoes=r[2], nivel=r[3])
        return None

    @staticmethod
    def buscar_por_nome(nome):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, permissoes, nivel FROM cargos WHERE LOWER(nome) = LOWER(?)", (nome.strip(),))
        r = cursor.fetchone()
        conn.close()
        if r:
            return Cargo(id=r[0], nome=r[1], permissoes=r[2], nivel=r[3])
        return None

    @staticmethod
    def salvar(cargo: Cargo):
        conn = conectar_bd()
        cursor = conn.cursor()
        if not cargo.nome.strip():
            conn.close()
            raise ValueError("O nome do cargo não pode ficar vazio.")
        if cargo.nivel <= 0 or cargo.nivel >= 1_000_000:
            conn.close()
            raise ValueError("O nível do cargo deve estar entre 1 e 999999.")
        if cargo.tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("A permissão de administrador principal é reservada ao dono.")
        cursor.execute("INSERT INTO cargos (nome, permissoes, nivel) VALUES (?, ?, ?)",
                       (cargo.nome.strip(), cargo.to_json(), cargo.nivel))
        novo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        cargo.id = novo_id
        return cargo

    @staticmethod
    def atualizar(cargo_id: int, nome: str, novas_permissoes: list, nivel: int):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT permissoes FROM cargos WHERE id = ?", (cargo_id,))
        existente = cursor.fetchone()
        if not existente:
            conn.close()
            raise ValueError("O cargo selecionado não existe.")
        if Cargo("", existente[0]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O cargo do dono não pode ser alterado.")
        if not nome.strip() or nivel <= 0 or nivel >= 1_000_000:
            conn.close()
            raise ValueError("Informe nome e nível entre 1 e 999999.")
        cursor.execute(
            "SELECT 1 FROM cargos WHERE LOWER(nome) = LOWER(?) AND id != ?",
            (nome.strip(), cargo_id),
        )
        if cursor.fetchone():
            conn.close()
            raise ValueError("Já existe um cargo com esse nome.")
        if Cargo("", novas_permissoes).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("A permissão de administrador principal é reservada ao dono.")
        cursor.execute("UPDATE cargos SET nome = ?, permissoes = ?, nivel = ? WHERE id = ?",
                       (nome.strip(), json.dumps(novas_permissoes), nivel, cargo_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(cargo_id: int):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT permissoes FROM cargos WHERE id = ?", (cargo_id,))
        existente = cursor.fetchone()
        if not existente:
            conn.close()
            raise ValueError("O cargo selecionado não existe.")
        if Cargo("", existente[0]).tem_permissao("cargos_gerenciar"):
            conn.close()
            raise ValueError("O cargo do dono não pode ser excluído.")
        cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE cargo_id = ?", (cargo_id,))
        if cursor.fetchone()[0]:
            conn.close()
            raise ValueError("Reatribua os funcionários antes de excluir este cargo.")
        cursor.execute("DELETE FROM cargos WHERE id = ?", (cargo_id,))
        conn.commit()
        conn.close()
