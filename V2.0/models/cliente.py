class Cliente:
    """Representa um cliente com dados cadastrais."""
    def __init__(self, cpf, nome, endereco="", telefone="", id=None):
        self.id = id
        self.cpf = str(cpf).strip()
        self.nome = nome.strip() if nome else ""
        self.endereco = endereco.strip() if endereco else ""
        self.telefone = telefone.strip() if telefone else ""

    def __repr__(self):
        return f"<Cliente {self.cpf}: {self.nome}>"
