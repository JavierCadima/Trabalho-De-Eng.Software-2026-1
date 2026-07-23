import sys
from PyQt6.QtWidgets import (QMainWindow, QTabWidget)

from views.tab_vendas import TabVendas
from views.tab_estoque import TabEstoque
from views.tab_clientes import TabClientes
from views.tab_gerenciador_vendas import TabGerenciadorVendas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão - Auto Mecânica & Baterias")
        self.setGeometry(80, 80, 1180, 720)

        # Container Principal de Abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Instância das Abas
        self.tab_vendas = TabVendas()
        self.tab_estoque = TabEstoque()
        self.tab_clientes = TabClientes()
        self.tab_gerenciador = TabGerenciadorVendas()

        # Adiciona as Abas ao Menu
        self.tabs.addTab(self.tab_vendas, "🛒 Frente de Balcão (Vendas)")
        self.tabs.addTab(self.tab_estoque, "📦 Gestão de Estoque")
        self.tabs.addTab(self.tab_clientes, "👥 Cadastro de Clientes")
        self.tabs.addTab(self.tab_gerenciador, "📈 Gerenciador de Vendas")

        # Conecta a troca de abas para atualizar dados automaticamente
        self.tabs.currentChanged.connect(self._ao_mudar_aba)

    def _ao_mudar_aba(self, index):
        # Quando alterna para a aba de Vendas, recarrega os clientes no ComboBox
        if index == 0:
            self.tab_vendas.carregar_clientes()
        # Quando alterna para a aba de Estoque, recarrega a tabela de baterias
        elif index == 1:
            self.tab_estoque.carregar_produtos()
        # Quando alterna para Clientes, recarrega a tabela
        elif index == 2:
            self.tab_clientes.carregar_clientes()
        elif index == 3:
            self.tab_gerenciador.carregar_dados()