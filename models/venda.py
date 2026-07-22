from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ItemVenda:
    produto_id: int
    quantidade: int
    numero_serie: str
    entregou_sucata: bool
    preco_aplicado: float
    categoria: str
    meses_garantia: int = 18

@dataclass
class VendaDTO:
    forma_pagamento: str
    desconto: float
    itens: List[ItemVenda]
    cliente_id: Optional[int] = None