# TESTE
import sys
import os
import traceback

# 1. Banco de Dados e Schema
from database.schema import init_db
from database.connection import get_connection

# 2. Models
from models.produto import Produto
from models.venda import VendaDTO, ItemVenda

# 3. Repositórios
from repositories.produto_repository import ProdutoRepository
from repositories.venda_repository import VendaRepository

# 4. Serviços (Regras de Negócio)
from services.venda_service import VendaService
from services.garantia_service import GarantiaService
from services.relatorio_service import RelatorioService

# 5. Interface Gráfica Unificada (Abas: Vendas, Estoque, Clientes)
from PyQt6.QtWidgets import QApplication, QMessageBox
from views.app_main import MainWindow


def hook_excecoes(exctype, value, tb):
    """
    Captura exceções não tratadas durante a execução da interface gráfica (PyQt)
    e exibe uma mensagem com o traceback em vez de fechar a aplicação repentinamente.
    """
    mensagem_erro = "".join(traceback.format_exception(exctype, value, tb))
    print("\n[ERRO NA INTERFACE CAPTURADO]:\n", mensagem_erro)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Erro no Processamento")
    msg.setText("Ocorreu um erro ao executar esta operação na interface:")
    msg.setDetailedText(mensagem_erro)
    msg.exec()


def executar_teste_backend():
    """
    Executa uma bateria completa de testes em modo texto (CLI/Headless)
    para validar o banco, serviços, baixas de estoque e geração de PDF.
    """
    print("\n" + "="*50)
    print(" INICIANDO ROTINA DE TESTES DO BACKEND (HEADLESS)")
    print("="*50 + "\n")

    # A. Inicializa o banco
    init_db()
    print("✓ [1/6] Banco de dados e schema inicializados.")

    # B. Instancia Repositórios e Serviços
    prod_repo = ProdutoRepository()
    venda_service = VendaService()
    garantia_service = GarantiaService()
    relatorio_service = RelatorioService()

    # C. Cadastra produtos no estoque
    id_moura = prod_repo.salvar(Produto(
        nome="Bateria Moura 60Ah - Polo Direito",
        marca="Moura",
        categoria="Carro",
        amperagem=60,
        preco_venda=520.00,
        preco_com_troca=440.00,
        estoque_atual=10
    ))

    id_heliar = prod_repo.salvar(Produto(
        nome="Bateria Heliar 150Ah Heavy Duty",
        marca="Heliar",
        categoria="Caminhao_Onibus",
        amperagem=150,
        preco_venda=1100.00,
        preco_com_troca=950.00,
        estoque_atual=5
    ))

    print(f"✓ [2/6] Produtos cadastrados com sucesso:")
    print(f"      - ID {id_moura}: Moura 60Ah (Estoque: 10)")
    print(f"      - ID {id_heliar}: Heliar 150Ah (Estoque: 5)")

    # D. Simula uma venda de balcão com múltiplos itens e sucata
    carrinho = [
        ItemVenda(
            produto_id=id_moura,
            quantidade=1,
            numero_serie="MOURA-2026-9988",
            entregou_sucata=True,
            preco_aplicado=440.00,
            categoria="Carro"
        ),
        ItemVenda(
            produto_id=id_heliar,
            quantidade=2,
            numero_serie="HELIAR-2026-1122",
            entregou_sucata=True,
            preco_aplicado=950.00,
            categoria="Caminhao_Onibus"
        )
    ]

    nova_venda = VendaDTO(
        forma_pagamento="Pix",
        desconto=40.00,
        itens=carrinho,
        cliente_id=None  # Compatível com a nova estrutura do VendaDTO
    )

    resultado = venda_service.processar_venda(nova_venda)
    print(f"\n✓ [3/6] Venda #{resultado['venda_id']} processada:")
    print(f"      - Total com Desconto: R$ {resultado['total']:.2f}")

    # E. Checa baixa no estoque
    prod_moura = prod_repo.buscar_por_id(id_moura)
    print(f"✓ [4/6] Estoque Moura 60Ah atualizado para: {prod_moura['estoque_atual']} un")

    # F. Consulta Garantia por Número de Série
    status_garantia = garantia_service.consultar_garantia("MOURA-2026-9988")
    print(f"✓ [5/6] Checagem de Garantia N/S 'MOURA-2026-9988':")
    print(f"      - Válida? {status_garantia.get('em_garantia')}")
    print(f"      - Validade: {status_garantia.get('validade_garantia')}")

    # G. Geração do Relatório PDF
    caminho_pdf = relatorio_service.gerar_pdf_fechamento()
    print(f"✓ [6/6] Relatório Gerencial em PDF emitido:")
    print(f"      - Caminho: {os.path.abspath(caminho_pdf)}")

    print("\n" + "="*50)
    print(" TESTES CONCLUÍDOS COM SUCESSO!")
    print("="*50 + "\n")


def iniciar_interface_grafica():
    """Inicializa o banco de dados e abre a janela principal com menu de abas."""
    # Define o tratador global para evitar crashes na GUI
    sys.excepthook = hook_excecoes

    init_db()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Tema limpo e consistente no Windows
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def main():
    # Se passar a flag '--test' no terminal, roda a rotina headless no backend
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        executar_teste_backend()
    else:
        iniciar_interface_grafica()


if __name__ == "__main__":
    main()
