from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox)
from repositories.produto_repository import ProdutoRepository

class TabEstoque(QWidget):
    def __init__(self):
        super().__init__()
        self.produto_repo = ProdutoRepository()
        self.produto_selecionado_id = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()

        # ================= FORMULÁRIO (ESQUERDA) =================
        form_layout = QVBoxLayout()
        self.lbl_titulo_form = QLabel("<b>Cadastrar / Editar Produto</b>")
        form_layout.addWidget(self.lbl_titulo_form)

        form = QFormLayout()
        self.input_nome = QLineEdit()
        self.input_marca = QLineEdit()
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Carro", "Moto", "Caminhao_Onibus", "Nautica"])
        
        self.spin_amperagem = QSpinBox()
        self.spin_amperagem.setRange(1, 300)
        self.spin_amperagem.setValue(60)

        self.spin_preco_venda = QDoubleSpinBox()
        self.spin_preco_venda.setRange(0.0, 10000.0)
        self.spin_preco_venda.setPrefix("R$ ")

        self.spin_preco_troca = QDoubleSpinBox()
        self.spin_preco_troca.setRange(0.0, 10000.0)
        self.spin_preco_troca.setPrefix("R$ ")

        self.spin_estoque = QSpinBox()
        self.spin_estoque.setRange(0, 1000)

        form.addRow("Nome/Modelo:", self.input_nome)
        form.addRow("Marca:", self.input_marca)
        form.addRow("Categoria:", self.combo_categoria)
        form.addRow("Amperagem (Ah):", self.spin_amperagem)
        form.addRow("Preço Normal:", self.spin_preco_venda)
        form.addRow("Preço c/ Troca (Sucata):", self.spin_preco_troca)
        form.addRow("Qtd. Estoque:", self.spin_estoque)

        form_layout.addLayout(form)

        # Botões do Form
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("💾 Salvar")
        self.btn_salvar.setStyleSheet("background-color: #2F855A; color: white; font-weight: bold; padding: 6px;")
        self.btn_salvar.clicked.connect(self._salvar_produto)

        self.btn_limpar = QPushButton("🧹 Limpar")
        self.btn_limpar.clicked.connect(self._limpar_formulario)

        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_limpar)
        form_layout.addLayout(btn_layout)

        form_layout.addStretch()

        # ================= TABELA DE LISTAGEM (DIREITA) =================
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("<b>Estoque Atual</b>"))

        self.tabela = QTableWidget(0, 8)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Marca", "Categoria", "Amperagem", "Preço Normal", "Preço c/ Troca", "Estoque"
        ])
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.cellClicked.connect(self._carregar_produto_para_edicao)
        table_layout.addWidget(self.tabela)

        # Botão Excluir abaixo da tabela
        self.btn_deletar = QPushButton("🗑️ Deletar Produto Selecionado")
        self.btn_deletar.setStyleSheet("background-color: #C53030; color: white; font-weight: bold; padding: 6px;")
        self.btn_deletar.clicked.connect(self._deletar_produto)
        table_layout.addWidget(self.btn_deletar)

        layout.addLayout(form_layout, 35)
        layout.addLayout(table_layout, 65)
        self.setLayout(layout)

        self.carregar_produtos()

    def carregar_produtos(self):
        self.tabela.setRowCount(0)
        try:
            produtos = self.produto_repo.listar_todos()
            for row, p in enumerate(produtos):
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                self.tabela.setItem(row, 1, QTableWidgetItem(str(p["nome"])))
                self.tabela.setItem(row, 2, QTableWidgetItem(str(p["marca"])))
                self.tabela.setItem(row, 3, QTableWidgetItem(str(p["categoria"])))
                self.tabela.setItem(row, 4, QTableWidgetItem(f"{p['amperagem']} Ah"))
                self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {p['preco_venda']:.2f}"))
                self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {p['preco_com_troca']:.2f}"))
                self.tabela.setItem(row, 7, QTableWidgetItem(str(p["estoque_atual"])))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao listar estoque: {e}")

    def _salvar_produto(self):
        nome = self.input_nome.text().strip()
        marca = self.input_marca.text().strip()

        if not nome or not marca:
            QMessageBox.warning(self, "Aviso", "Nome e Marca são obrigatórios!")
            return

        dados = {
            "nome": nome,
            "marca": marca,
            "categoria": self.combo_categoria.currentText(),
            "amperagem": self.spin_amperagem.value(),
            "preco_venda": self.spin_preco_venda.value(),
            "preco_com_troca": self.spin_preco_troca.value(),
            "estoque_atual": self.spin_estoque.value()
        }

        try:
            if self.produto_selecionado_id:
                dados["id"] = self.produto_selecionado_id
                self.produto_repo.atualizar(dados)
                QMessageBox.information(self, "Sucesso", "Produto atualizado!")
            else:
                self.produto_repo.salvar(dados)
                QMessageBox.information(self, "Sucesso", "Produto cadastrado!")

            self._limpar_formulario()
            self.carregar_produtos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def _carregar_produto_para_edicao(self, row, col):
        self.produto_selecionado_id = int(self.tabela.item(row, 0).text())
        self.input_nome.setText(self.tabela.item(row, 1).text())
        self.input_marca.setText(self.tabela.item(row, 2).text())
        self.combo_categoria.setCurrentText(self.tabela.item(row, 3).text())
        
        amp = self.tabela.item(row, 4).text().replace(" Ah", "")
        self.spin_amperagem.setValue(int(amp))

        preco_venda = float(self.tabela.item(row, 5).text().replace("R$ ", ""))
        preco_troca = float(self.tabela.item(row, 6).text().replace("R$ ", ""))
        self.spin_preco_venda.setValue(preco_venda)
        self.spin_preco_troca.setValue(preco_troca)

        self.spin_estoque.setValue(int(self.tabela.item(row, 7).text()))
        self.lbl_titulo_form.setText(f"<b>Editar Produto (ID: {self.produto_selecionado_id})</b>")

    def _deletar_produto(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto na tabela para deletar.")
            return

        p_id = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()

        resposta = QMessageBox.question(
            self, "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o produto '{nome}' (ID: {p_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self.produto_repo.deletar(p_id)
                QMessageBox.information(self, "Sucesso", "Produto removido com sucesso!")
                self._limpar_formulario()
                self.carregar_produtos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao deletar: {e}")

    def _limpar_formulario(self):
        self.produto_selecionado_id = None
        self.input_nome.clear()
        self.input_marca.clear()
        self.spin_amperagem.setValue(60)
        self.spin_preco_venda.setValue(0.0)
        self.spin_preco_troca.setValue(0.0)
        self.spin_estoque.setValue(0)
        self.lbl_titulo_form.setText("<b>Cadastrar / Editar Produto</b>")