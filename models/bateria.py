class Bateria:
    def __init__(self, marca, modelo, amperagem, cca, voltagem, aplicacao, 
                 garantia_meses, quantidade, preco_custo, preco_venda, 
                 preco_minimo, valor_carcaca, id=None):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.amperagem = amperagem
        self.cca = cca
        self.voltagem = voltagem
        self.aplicacao = aplicacao
        self.garantia_meses = garantia_meses
        self.quantidade = quantidade
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.preco_minimo = preco_minimo
        self.valor_carcaca = valor_carcaca