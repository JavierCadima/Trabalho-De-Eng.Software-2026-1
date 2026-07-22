from database.schema import init_db
from models.produto import Produto
from models.venda import VendaDTO, ItemVenda
from repositories.produto_repository import ProdutoRepository
from services.venda_service import VendaService
from services.garantia_service import GarantiaService

def main():
    # 1. Inicializa o banco de dados
    init_db()
    print("✓ Banco de Dados Inicializado.")

    # 2. Cadastra um produto para teste
    prod_repo = ProdutoRepository()
    id_bateria = prod_repo.salvar(Produto(
        nome="Bateria Moura 60Ah",
        marca="Moura",
        categoria="Carro",
        amperagem=60,
        preco_venda=520.00,
        preco_com_troca=440.00,
        estoque_atual=10
    ))
    print(f"✓ Bateria Cadastrada com ID: {id_bateria}")

    # 3. Realiza uma venda no balcão via VendaService
    venda_service = VendaService()
    carrinho = [
        ItemVenda(
            produto_id=id_bateria,
            quantidade=1,
            numero_serie="MOURA-2026-9988",
            entregou_sucata=True,
            preco_aplicado=440.00,
            categoria="Carro"
        )
    ]

    nova_venda = VendaDTO(forma_pagamento="Pix", desconto=10.00, itens=carrinho)
    resultado = venda_service.processar_venda(nova_venda)
    print(f"✓ Venda #{resultado['venda_id']} realizada com sucesso! Total: R$ {resultado['total']:.2f}")

    # 4. Testa a consulta de garantia
    garantia_service = GarantiaService()
    status_garantia = garantia_service.consultar_garantia("MOURA-2026-9988")
    print(f"✓ Status da Garantia: {status_garantia}")

if __name__ == "__main__":
    main()