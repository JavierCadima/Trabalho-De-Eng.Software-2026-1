# models/desconto.py

class RegraDesconto:
    """
    Define regras de desconto flexíveis para a loja.
    Exemplos de tipo_regra: 'CNPJ', 'CPF', 'PIX', 'DINHEIRO', 'QTD_MINIMA'
    """
    def __init__(self, tipo_regra: str, percentual: float = 0.0, min_itens: int = 1, ativo: bool = True):
        self.tipo_regra = tipo_regra
        self.percentual = percentual
        self.min_itens = min_itens
        self.ativo = ativo

    def calcular_desconto(self, subtotal: float, qtd_total_itens: int, tipo_cliente: str, forma_pagamento: str) -> float:
        if not self.ativo or subtotal <= 0:
            return 0.0

        # Regra CNPJ vs CPF
        if self.tipo_regra == "CNPJ" and tipo_cliente == "CNPJ":
            return subtotal * (self.percentual / 100.0)
            
        if self.tipo_regra == "CPF" and tipo_cliente == "CPF":
            return subtotal * (self.percentual / 100.0)

        # Regra de Pagamento (PIX / DINHEIRO)
        if self.tipo_regra == "PIX" and forma_pagamento.upper() == "PIX":
            return subtotal * (self.percentual / 100.0)

        if self.tipo_regra == "DINHEIRO" and forma_pagamento.upper() == "DINHEIRO":
            return subtotal * (self.percentual / 100.0)

        # Regra por Volume / Quantidade Mínima
        if self.tipo_regra == "QTD_MINIMA" and qtd_total_itens >= self.min_itens:
            return subtotal * (self.percentual / 100.0)

        return 0.0