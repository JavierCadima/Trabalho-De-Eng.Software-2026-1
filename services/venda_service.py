from database.connection import get_connection
from models.venda import VendaDTO
from repositories.produto_repository import ProdutoRepository
from repositories.venda_repository import VendaRepository
from repositories.sucata_repository import SucataRepository

class VendaService:
    def __init__(self):
        self.produto_repo = ProdutoRepository()
        self.venda_repo = VendaRepository()
        self.sucata_repo = SucataRepository()

    def processar_venda(self, venda: VendaDTO) -> dict:
        if not venda.itens:
            raise ValueError("O carrinho de compras não pode estar vazio.")

        conn = get_connection()
        try:
            conn.execute("BEGIN TRANSACTION;")

            subtotal = 0.0
            for item in venda.itens:
                prod = self.produto_repo.buscar_por_id(item.produto_id)
                if not prod:
                    raise ValueError(f"Produto ID {item.produto_id} não encontrado.")
                
                if prod["estoque_atual"] < item.quantidade:
                    raise ValueError(f"Estoque insuficiente para '{prod['nome']}'. Disponível: {prod['estoque_atual']}")

                subtotal += item.preco_aplicado * item.quantidade

            total = max(0.0, subtotal - venda.desconto)

            # 1. Registra a venda
            venda_id = self.venda_repo.registrar_venda_transacao(conn, venda, subtotal, total)

            # 2. Processa itens, baixa estoque e contabiliza sucata
            for item in venda.itens:
                self.venda_repo.registrar_item(conn, venda_id, item)
                self.produto_repo.dar_baixa_estoque(conn, item.produto_id, item.quantidade)
                
                if item.entregou_sucata:
                    self.sucata_repo.incrementar_sucata(conn, item.quantidade, item.categoria)

            conn.commit()
            return {"sucesso": True, "venda_id": venda_id, "total": total}

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()