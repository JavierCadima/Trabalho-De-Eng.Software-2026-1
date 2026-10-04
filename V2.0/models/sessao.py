class SessaoSistema:
    """Gerencia o operador logado no sistema e suas permissões."""
    _operador_atual = None

    @classmethod
    def definir_operador(cls, funcionario):
        cls._operador_atual = funcionario

    @classmethod
    def obter_operador(cls):
        return cls._operador_atual

    @classmethod
    def tem_permissao(cls, codigo_permissao: str) -> bool:
        if not cls._operador_atual:
            return False
        return cls._operador_atual.tem_permissao(codigo_permissao)

    @classmethod
    def is_administrador_principal(cls) -> bool:
        if not cls._operador_atual:
            return False
        return cls._operador_atual.is_administrador_principal()
