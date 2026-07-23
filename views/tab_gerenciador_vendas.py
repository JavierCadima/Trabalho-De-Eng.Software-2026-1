from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QGroupBox)
from repositories.venda_repository import VendaRepository

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
except ImportError:
    FigureCanvas = None
    plt = None

class TabGerenciadorVendas(QWidget):
    def __init__(self):
        super().__init__()
        self.venda_repo = VendaRepository()
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<h2><b>Histórico de Vendas (Últimos 3 Meses)</b></h2>"))

        self.tabela_vendas = QTableWidget(0, 6)
        self.tabela_vendas.setHorizontalHeaderLabels(["ID", "Data", "Cliente", "Forma Pagto", "Desconto", "Total"])
        self.tabela_vendas.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.tabela_vendas)

        right_layout = QVBoxLayout()
        box_grafico = QGroupBox("📊 Top Baterias Mais Vendidas")
        grafico_box_layout = QVBoxLayout()

        if FigureCanvas is None or plt is None:
            grafico_box_layout.addWidget(QLabel("Instale o pacote 'matplotlib' para habilitar o gráfico de vendas."))
        else:
            self.figure, self.ax = plt.subplots(figsize=(5, 4))
            self.canvas = FigureCanvas(self.figure)
            grafico_box_layout.addWidget(self.canvas)

        box_grafico.setLayout(grafico_box_layout)

        right_layout.addWidget(box_grafico)

        layout.addLayout(left_layout, 60)
        layout.addLayout(right_layout, 40)
        self.setLayout(layout)

        self.carregar_dados()

    def carregar_dados(self):
        self._carregar_tabela_vendas()
        self._gerar_grafico_mais_vendidas()

    def _carregar_tabela_vendas(self):
        self.tabela_vendas.setRowCount(0)
        vendas = self.venda_repo.listar_vendas_ultimos_3_meses()

        for row, v in enumerate(vendas):
            self.tabela_vendas.insertRow(row)
            self.tabela_vendas.setItem(row, 0, QTableWidgetItem(str(v[0])))
            self.tabela_vendas.setItem(row, 1, QTableWidgetItem(str(v[1])))
            self.tabela_vendas.setItem(row, 2, QTableWidgetItem(str(v[2])))
            self.tabela_vendas.setItem(row, 3, QTableWidgetItem(str(v[3])))
            self.tabela_vendas.setItem(row, 4, QTableWidgetItem(f"R$ {v[4]:.2f}"))
            self.tabela_vendas.setItem(row, 5, QTableWidgetItem(f"R$ {v[5]:.2f}"))

    def _gerar_grafico_mais_vendidas(self):
        if FigureCanvas is None or plt is None:
            return

        self.ax.clear()
        dados = self.venda_repo.obter_ranking_baterias_mais_vendidas(limite=5)

        if not dados:
            self.ax.text(0.5, 0.5, "Nenhuma venda registrada", ha='center', va='center')
        else:
            produtos = [d[0] for d in dados]
            quantidades = [d[1] for d in dados]
            produtos.reverse()
            quantidades.reverse()

            bars = self.ax.barh(produtos, quantidades, color='#2B6CB0')
            self.ax.set_xlabel('Unidades Vendidas')
            self.ax.set_title('Baterias com Maior Saída')
            self.ax.bar_label(bars, padding=3)
            self.figure.tight_layout()

        self.canvas.draw()
