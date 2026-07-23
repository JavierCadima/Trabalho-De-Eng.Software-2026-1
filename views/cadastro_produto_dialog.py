# views/cadastro_produto_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox)
from models.produto import Produto
from repositories.produto_repository import ProdutoRepository

class CadastroProdutoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Produto / Bateria")
        self.setFixedSize(380, 320)
        self.repo = ProdutoRepository()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Ex: Bateria Moura 60Ah")

        self.input_marca = QLineEdit()
        self.input_marca.setPlaceholderText("Ex: Moura, Heliar, Tudor")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Carro", "Moto", "Caminhao_Onibus", "Nautica"])

        self.input_amperagem = QLineEdit()
        self.input_amperagem.setPlaceholderText("Ex: 60")

        self.input_preco_venda = QLineEdit()
        self.input_preco_venda.setPlaceholderText("Ex: 520.00")

        self.input_preco_troca = QLineEdit()
        self.input_preco_troca.setPlaceholderText("Ex: 440.00")

        self.input_estoque = QLineEdit()
        self.input_estoque.setPlaceholderText("Ex: 10")

        form.addRow("Nome:", self.input_nome)
        form.addRow("Marca:", self.input_marca)
        form.addRow("Categoria:", self.combo_categoria)
        form.addRow("Amperagem (Ah):", self.input_amperagem)
        form.addRow("Preço Sem Troca (R$):", self.input_preco_venda)
        form.addRow("Preço Com Troca (R$):", self.input_preco_troca)
        form.addRow("Estoque Inicial:", self.input_estoque)

        layout.addLayout(form)

        btn_salvar = QPushButton("Salvar Produto")
        btn_salvar.setStyleSheet("background-color: #2F855A; color: white; font-weight: bold; padding: 8px;")
        btn_salvar.clicked.connect(self._salvar_produto)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

    def _salvar_produto(self):
        try:
            produto = Produto(
                nome=self.input_nome.text().strip(),
                marca=self.input_marca.text().strip(),
                categoria=self.combo_categoria.currentText(),
                amperagem=int(self.input_amperagem.text()),
                preco_venda=float(self.input_preco_venda.text().replace(',', '.')),
                preco_com_troca=float(self.input_preco_troca.text().replace(',', '.')),
                estoque_atual=int(self.input_estoque.text())
            )

            novo_id = self.repo.salvar(produto)
            QMessageBox.information(self, "Sucesso", f"Produto cadastrado com sucesso! ID: {novo_id}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao cadastrar: {str(e)}")