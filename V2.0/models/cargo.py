import json

class Cargo:
    """Representa um cargo com lista customizável de permissões."""
    def __init__(self, nome, permissoes=None, id=None, nivel=1):
        self.id = id
        self.nome = nome
        self.nivel = int(nivel)
        if permissoes is None:
            self.permissoes = []
        elif isinstance(permissoes, str):
            try:
                self.permissoes = json.loads(permissoes)
            except Exception:
                self.permissoes = [p.strip() for p in permissoes.split(',') if p.strip()]
        else:
            self.permissoes = list(permissoes)

    def tem_permissao(self, codigo_permissao: str) -> bool:
        """Verifica se o cargo possui a permissão informada."""
        return codigo_permissao in self.permissoes or "tudo" in self.permissoes

    def to_json(self) -> str:
        return json.dumps(self.permissoes)

    def __repr__(self):
        return f"<Cargo {self.id}: {self.nome} ({len(self.permissoes)} permissões)>"
