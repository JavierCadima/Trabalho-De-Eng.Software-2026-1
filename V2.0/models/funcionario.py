class Funcionario:
    """Representa um funcionário do sistema vinculado a um Cargo."""
    def __init__(
        self, matricula, nome, cargo, id=None, ativo=1,
        senha_hash=None, senha_salt=None
    ):
        self.id = id
        self.matricula = str(matricula).strip()
        self.nome = nome
        self.cargo = cargo  # Instância de Cargo
        self.ativo = ativo
        self.senha_hash = senha_hash
        self.senha_salt = senha_salt

    def tem_permissao(self, codigo_permissao: str) -> bool:
        """Delega a verificação de permissão para o cargo associado."""
        if not self.ativo or not self.cargo:
            return False
        return self.cargo.tem_permissao(codigo_permissao)

    def is_administrador_principal(self) -> bool:
        """Verifica se o funcionário é o Administrador Principal / Dono."""
        return bool(self.cargo and self.cargo.tem_permissao("cargos_gerenciar"))

    def __repr__(self):
        cargo_nome = self.cargo.nome if self.cargo else "Sem Cargo"
        return f"<Funcionario {self.matricula}: {self.nome} ({cargo_nome})>"
