class ItemVenda:
    def __init__(
        self, 
        produto_id, 
        quantidade=1, 
        preco_aplicado=0.0, 
        entregou_sucata=True, 
        meses_garantia=12, 
        numero_serie="", 
        nome_produto="",
        categoria=""
    ):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_aplicado = preco_aplicado
        self.entregou_sucata = entregou_sucata
        self.meses_garantia = meses_garantia
        self.numero_serie = numero_serie if numero_serie is not None else ""
        self.nome_produto = nome_produto
        self.categoria = categoria


class Venda:
    def __init__(
        self, 
        cliente_id=None, 
        forma_pagamento="Dinheiro", 
        valor_total=0.0, 
        bandeira_cartao=None, 
        parcelas=1, 
        desconto=0.0, 
        itens=None
    ):
        self.cliente_id = cliente_id
        self.forma_pagamento = forma_pagamento
        self.bandeira_cartao = bandeira_cartao if forma_pagamento == "Cartão de Crédito" else None
        self.parcelas = parcelas
        self.desconto = desconto
        self.valor_total = valor_total
        self.itens = itens if itens is not None else []


# DTO (Data Transfer Object) utilizado pelos serviços e testes do backend
class VendaDTO:
    def __init__(
        self, 
        forma_pagamento="Dinheiro", 
        desconto=0.0, 
        itens=None, 
        cliente_id=None, 
        bandeira_cartao=None, 
        parcelas=1,
        valor_total=0.0
    ):
        self.cliente_id = cliente_id
        self.forma_pagamento = forma_pagamento
        self.bandeira_cartao = bandeira_cartao
        self.parcelas = parcelas
        self.desconto = desconto
        self.valor_total = valor_total
        self.itens = itens if itens is not None else []