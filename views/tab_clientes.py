from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFormLayout, QGroupBox, QDoubleSpinBox)
from repositories.cliente_repository import ClienteRepository
from repositories.configuracao_repository import ConfiguracaoRepository

class TabClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.cliente_repo = ClienteRepository()
        self.config_repo = ConfiguracaoRepository()
        self.cliente_selecionado_id = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()

        # FORMULÁRIO (ESQUERDA)
        form_layout = QVBoxLayout()
        self.lbl_titulo = QLabel("<b>Cadastrar / Editar Cliente</b>")
        form_layout.addWidget(self.lbl_titulo)

        form = QFormLayout()
        self.input_nome = QLineEdit()
        self.input_cpf_cnpj = QLineEdit()
        self.input_cpf_cnpj.setPlaceholderText("CPF ou CNPJ (ex: 00.000.000/0001-00)")
        self.input_telefone = QLineEdit()
        self.input_veiculo = QLineEdit()
        self.input_endereco = QLineEdit()

        form.addRow("Nome / Razão Social:", self.input_nome)
        form.addRow("CPF / CNPJ:", self.input_cpf_cnpj)
        form.addRow("Telefone:", self.input_telefone)
        form.addRow("Veículo / Placa:", self.input_veiculo)
        form.addRow("Endereço:", self.input_endereco)

        form_layout.addLayout(form)

        btn_box = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar")
        btn_salvar.setStyleSheet("background-color: #2F855A; color: white; font-weight: bold; padding: 6px;")
        btn_salvar.clicked.connect(self._salvar_cliente)

        btn_limpar = QPushButton("🧹 Limpar")
        btn_limpar.clicked.connect(self._limpar_form)

        btn_box.addWidget(btn_salvar)
        btn_box.addWidget(btn_limpar)
        form_layout.addLayout(btn_box)

        # CONFIGURAÇÃO DE DESCONTO CNPJ DA LOJA
        box_config = QGroupBox("Configuração da Loja")
        config_form = QFormLayout()
        self.spin_desconto_cnpj = QDoubleSpinBox()
        self.spin_desconto_cnpj.setRange(0.0, 100.0)
        self.spin_desconto_cnpj.setSuffix("%")
        self.spin_desconto_cnpj.setValue(self.config_repo.get_desconto_cnpj())

        btn_salvar_config = QPushButton("Salvar % Desconto CNPJ")
        btn_salvar_config.clicked.connect(self._salvar_config_cnpj)

        config_form.addRow("Desconto Padrão CNPJ:", self.spin_desconto_cnpj)
        config_form.addRow(btn_salvar_config)
        box_config.setLayout(config_form)
        form_layout.addWidget(box_config)

        form_layout.addStretch()

        # LISTAGEM (DIREITA)
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("<b>Clientes Cadastrados</b>"))

        self.tabela = QTableWidget(0, 6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "CPF / CNPJ", "Telefone", "Veículo", "Endereço"])
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.cellClicked.connect(self._carregar_cliente_edicao)
        table_layout.addWidget(self.tabela)

        btn_deletar = QPushButton("🗑️ Deletar Cliente Selecionado")
        btn_deletar.setStyleSheet("background-color: #C53030; color: white; font-weight: bold; padding: 6px;")
        btn_deletar.clicked.connect(self._deletar_cliente)
        table_layout.addWidget(btn_deletar)

        layout.addLayout(form_layout, 40)
        layout.addLayout(table_layout, 60)
        self.setLayout(layout)

        self.carregar_clientes()

    def _salvar_config_cnpj(self):
        val = self.spin_desconto_cnpj.value()
        self.config_repo.set_desconto_cnpj(val)
        QMessageBox.information(self, "Sucesso", f"Desconto para CNPJ atualizado para {val:.1f}%!")

    def _salvar_cliente(self):
        nome = self.input_nome.text().strip()
        cpf_cnpj = self.input_cpf_cnpj.text().strip()

        if not nome or not cpf_cnpj:
            QMessageBox.warning(self, "Aviso", "Nome e CPF/CNPJ são obrigatórios!")
            return

        dados = {
            "nome": nome,
            "cpf_cnpj": cpf_cnpj,
            "telefone": self.input_telefone.text().strip(),
            "veiculo": self.input_veiculo.text().strip(),
            "endereco": self.input_endereco.text().strip()
        }

        try:
            if self.cliente_selecionado_id:
                dados["id"] = self.cliente_selecionado_id
                self.cliente_repo.atualizar(dados)
                QMessageBox.information(self, "Sucesso", "Cliente atualizado!")
            else:
                self.cliente_repo.salvar(dados)
                QMessageBox.information(self, "Sucesso", "Cliente cadastrado!")

            self._limpar_form()
            self.carregar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _carregar_cliente_edicao(self, row, col):
        self.cliente_selecionado_id = int(self.tabela.item(row, 0).text())
        self.input_nome.setText(self.tabela.item(row, 1).text())
        self.input_cpf_cnpj.setText(self.tabela.item(row, 2).text())
        self.input_telefone.setText(self.tabela.item(row, 3).text())
        self.input_veiculo.setText(self.tabela.item(row, 4).text())
        self.input_endereco.setText(self.tabela.item(row, 5).text())
        self.lbl_titulo.setText(f"<b>Editar Cliente (ID: {self.cliente_selecionado_id})</b>")

    def _deletar_cliente(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para excluir.")
            return

        c_id = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()

        res = QMessageBox.question(
            self, "Excluir Cliente", 
            f"Deseja excluir '{nome}' (ID: {c_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if res == QMessageBox.StandardButton.Yes:
            try:
                self.cliente_repo.deletar(c_id)
                QMessageBox.information(self, "Sucesso", "Cliente excluído!")
                self._limpar_form()
                self.carregar_clientes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def carregar_clientes(self):
        self.tabela.setRowCount(0)
        try:
            clientes = self.cliente_repo.listar_todos()
            for row, c in enumerate(clientes):
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(str(c["id"])))
                self.tabela.setItem(row, 1, QTableWidgetItem(c["nome"]))
                self.tabela.setItem(row, 2, QTableWidgetItem(c["cpf_cnpj"]))
                self.tabela.setItem(row, 3, QTableWidgetItem(c.get("telefone", "")))
                self.tabela.setItem(row, 4, QTableWidgetItem(c.get("veiculo", "")))
                self.tabela.setItem(row, 5, QTableWidgetItem(c.get("endereco", "")))
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")

    def _limpar_form(self):
        self.cliente_selecionado_id = None
        self.input_nome.clear()
        self.input_cpf_cnpj.clear()
        self.input_telefone.clear()
        self.input_veiculo.clear()
        self.input_endereco.clear()
        self.lbl_titulo.setText("<b>Cadastrar / Editar Cliente</b>")