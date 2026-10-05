class Venda:
    def __init__(self, bateria_id, cliente_cpf, numero_serie, data_venda, 
                 com_troca, valor_pago, forma_pagamento, garantia_ate, 
                 cliente_nome="", cliente_endereco="", id=None):
        self.id = id
        self.bateria_id = bateria_id
        self.cliente_cpf = cliente_cpf
        self.cliente_nome = cliente_nome
        self.cliente_endereco = cliente_endereco
        self.numero_serie = numero_serie
        self.data_venda = data_venda
        self.com_troca = com_troca
        self.valor_pago = valor_pago
        self.forma_pagamento = forma_pagamento
        self.garantia_ate = garantia_ate