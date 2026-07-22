from dataclasses import dataclass
from typing import Optional

@dataclass
class Produto:
    nome: str
    marca: str
    categoria: str
    amperagem: int
    preco_venda: float
    preco_com_troca: float
    estoque_atual: int
    id: Optional[int] = None