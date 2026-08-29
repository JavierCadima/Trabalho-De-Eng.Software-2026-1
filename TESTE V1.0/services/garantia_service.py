from datetime import datetime, timedelta
from repositories.venda_repository import VendaRepository

class GarantiaService:
    def __init__(self):
        self.venda_repo = VendaRepository()

    def consultar_garantia(self, numero_serie: str) -> dict:
        item = self.venda_repo.buscar_por_numero_serie(numero_serie)
        if not item:
            return {"encontrado": False, "mensagem": "Bateria não encontrada no histórico."}

        data_venda = datetime.strptime(item["data_venda"], "%Y-%m-%d %H:%M:%S")
        data_limite = data_venda + timedelta(days=item["meses_garantia"] * 30)
        em_garantia = datetime.now() <= data_limite

        return {
            "encontrado": True,
            "em_garantia": em_garantia,
            "produto": item["produto_nome"],
            "numero_serie": item["numero_serie"],
            "data_venda": item["data_venda"],
            "validade_garantia": data_limite.strftime("%Y-%m-%d")
        }