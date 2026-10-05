class TrocaGarantia:
    def __init__(self, venda_id, bateria_id, numero_serie_defeito, 
                 defeito_relatado, data_troca, status="Defeituosa (Aguardando Troca/Fábrica)", id=None):
        self.id = id
        self.venda_id = venda_id
        self.bateria_id = bateria_id
        self.numero_serie_defeito = numero_serie_defeito
        self.defeito_relatado = defeito_relatado
        self.data_troca = data_troca
        self.status = status