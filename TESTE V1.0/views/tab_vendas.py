from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox)
from repositories.produto_repository import ProdutoRepository
from repositories.cliente_repository import ClienteRepository
from repositories.configuracao_repository import ConfiguracaoRepository
from services.venda_service import VendaService
from models.venda import ItemVenda, VendaDTO


class TabVendas(QWidget):
    def __init__(self):
        super().__init__()
        self.produto_repo = ProdutoRepository()
        self.cliente_repo = ClienteRepository()
        self.config_repo = ConfiguracaoRepository()
        self.venda_service = VendaService()
        self.carrinho = []
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()

        # ESQUERDA: Formulário
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("<b>Cliente:</b>"))
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(self._calcular_desconto_automatico)
        left_layout.addWidget(self.combo_clientes)

        box_produto = QGroupBox("Adicionar Item")
        box_form = QVBoxLayout()

        box_form.addWidget(QLabel("Produto:"))
        self.combo_produtos = QComboBox()
        box_form.addWidget(self.combo_produtos)

        self.chk_sucata = QCheckBox("Entregou sucata (Preço c/ Troca)")
        self.chk_sucata.setChecked(True)
        box_form.addWidget(self.chk_sucata)

        box_form.addWidget(QLabel("Quantidade:"))
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setRange(1, 1000)
        self.spin_quantidade.setValue(1)
        box_form.addWidget(self.spin_quantidade)

        btn_add = QPushButton("➕ Adicionar ao Carrinho")
        btn_add.setStyleSheet("background-color: #2B6CB0; color: white; font-weight: bold; padding: 8px;")
        btn_add.clicked.connect(self._adicionar_ao_carrinho)
        box_form.addWidget(btn_add)

        box_produto.setLayout(box_form)
        left_layout.addWidget(box_produto)

        # Pagamento e Desconto
        box_pagamento = QGroupBox("Pagamento")
        box_pag_layout = QVBoxLayout()

        box_pag_layout.addWidget(QLabel("Forma de Pagamento:"))
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Pix", "Dinheiro", "Cartão de Débito", "Cartão de Crédito"])
        box_pag_layout.addWidget(self.combo_pagamento)
        self.combo_pagamento.currentIndexChanged.connect(self._calcular_desconto_automatico)

        box_pag_layout.addWidget(QLabel("Bandeira do Cartão:"))
        self.combo_bandeira = QComboBox()
        self.combo_bandeira.addItems(["Nenhum / Não se Aplica", "Visa", "Mastercard", "Elo", "Hipercard", "Amex"])
        box_pag_layout.addWidget(self.combo_bandeira)

        box_pag_layout.addWidget(QLabel("Desconto (R$):"))
        self.spin_desconto = QDoubleSpinBox()
        # PERMITE VALORES MAIORES QUE 4 DÍGITOS (Até R$ 999.999,00)
        self.spin_desconto.setRange(0.0, 999999.0)
        self.spin_desconto.setDecimals(2)
        self.spin_desconto.setPrefix("R$ ")
        self.spin_desconto.valueChanged.connect(self._atualizar_totais)
        box_pag_layout.addWidget(self.spin_desconto)

        box_pagamento.setLayout(box_pag_layout)
        left_layout.addWidget(box_pagamento)

        left_layout.addStretch()

        # DIREITA: Carrinho
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>Itens do Carrinho</b>"))

        self.tabela_carrinho = QTableWidget(0, 5)
        self.tabela_carrinho.setHorizontalHeaderLabels(["ID", "Produto", "Qtd", "Preço Unit.", "Subtotal"])
        self.tabela_carrinho.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.tabela_carrinho)

        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("<h2>Total:</h2>"))
        self.lbl_total = QLabel("<h2>R$ 0.00</h2>")
        self.lbl_total.setStyleSheet("color: #2F855A;")
        total_layout.addWidget(self.lbl_total)
        total_layout.addStretch()

        btn_finalizar = QPushButton("✅ Finalizar Venda")
        btn_finalizar.setStyleSheet("background-color: #2F855A; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        btn_finalizar.clicked.connect(self._finalizar_venda)
        total_layout.addWidget(btn_finalizar)

        right_layout.addLayout(total_layout)

        layout.addLayout(left_layout, 40)
        layout.addLayout(right_layout, 60)
        self.setLayout(layout)

        self.carregar_clientes()
        self.carregar_produtos()

    def carregar_clientes(self):
        self.combo_clientes.clear()
        self.combo_clientes.addItem("Cliente Avulso / Não Identificado", userData=None)
        clientes = self.cliente_repo.listar_todos()
        for c in clientes:
            self.combo_clientes.addItem(f"{c['nome']} (CPF/CNPJ: {c['cpf_cnpj']})", userData=c)

    def carregar_produtos(self):
        self.combo_produtos.clear()
        produtos = self.produto_repo.listar_todos()
        for p in produtos:
            self.combo_produtos.addItem(f"{p['nome']} - {p['marca']} | R$ {p['preco_com_troca']:.2f} (Estoque: {p['estoque_atual']})", userData=p['id'])

    def _calcular_desconto_automatico(self):
        subtotal = sum(item.quantidade * item.preco_aplicado for item in self.carrinho)
        if subtotal <= 0:
            self.spin_desconto.setValue(0.0)
            return

        qtd_total = sum(item.quantidade for item in self.carrinho)
        cliente_data = self.combo_clientes.currentData()
        tipo_cliente = "AVULSO"

        if cliente_data:
            doc = str(cliente_data.get("cpf_cnpj", "")).replace(".", "").replace("-", "").replace("/", "").strip()
            if len(doc) > 11:
                tipo_cliente = "CNPJ"
            elif len(doc) > 0:
                tipo_cliente = "CPF"

        forma_pagto = self.combo_pagamento.currentText().strip().upper()

        desc_cnpj = self.config_repo.get_desconto_cnpj()
        desc_cpf = self.config_repo.get_desconto_cpf()
        desc_pix = self.config_repo.get_desconto_pix()
        desc_dinheiro = self.config_repo.get_desconto_dinheiro()
        desc_qtd_min = self.config_repo.get_desconto_qtd_minima_percentual()
        qtd_min = self.config_repo.get_desconto_qtd_minima_qtd()

        percentual_aplicado = 0.0
        if tipo_cliente == "CNPJ":
            percentual_aplicado = max(percentual_aplicado, desc_cnpj)
        elif tipo_cliente == "CPF":
            percentual_aplicado = max(percentual_aplicado, desc_cpf)

        if forma_pagto == "PIX":
            percentual_aplicado = max(percentual_aplicado, desc_pix)
        elif forma_pagto == "DINHEIRO":
            percentual_aplicado = max(percentual_aplicado, desc_dinheiro)

        if qtd_total >= qtd_min:
            percentual_aplicado = max(percentual_aplicado, desc_qtd_min)

        desconto_calculado = subtotal * (percentual_aplicado / 100.0)
        self.spin_desconto.setValue(desconto_calculado)

    def _adicionar_ao_carrinho(self):
        try:
            produto_id = self.combo_produtos.currentData()
            if not produto_id:
                QMessageBox.warning(self, "Aviso", "Selecione um produto.")
                return

            produto = self.produto_repo.buscar_por_id(produto_id)
            if not produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado.")
                return

            qtd = self.spin_quantidade.value()
            if qtd > produto["estoque_atual"]:
                QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque disponível: {produto['estoque_atual']} un.")
                return

            entregou_sucata = self.chk_sucata.isChecked()
            preco_aplicado = produto["preco_com_troca"] if entregou_sucata else produto["preco_venda"]

            item = ItemVenda(
                produto_id=produto["id"],
                quantidade=qtd,
                preco_aplicado=preco_aplicado,
                entregou_sucata=entregou_sucata,
                meses_garantia=produto.get("meses_garantia", 12),
                nome_produto=produto["nome"]
            )

            self.carrinho.append(item)
            self._atualizar_tabela_carrinho()
            self._calcular_desconto_automatico()
            self._atualizar_totais()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _atualizar_tabela_carrinho(self):
        self.tabela_carrinho.setRowCount(0)
        for row, item in enumerate(self.carrinho):
            self.tabela_carrinho.insertRow(row)
            self.tabela_carrinho.setItem(row, 0, QTableWidgetItem(str(item.produto_id)))
            self.tabela_carrinho.setItem(row, 1, QTableWidgetItem(item.nome_produto))
            self.tabela_carrinho.setItem(row, 2, QTableWidgetItem(str(item.quantidade)))
            self.tabela_carrinho.setItem(row, 3, QTableWidgetItem(f"R$ {item.preco_aplicado:.2f}"))
            self.tabela_carrinho.setItem(row, 4, QTableWidgetItem(f"R$ {(item.quantidade * item.preco_aplicado):.2f}"))

    def _atualizar_totais(self):
        subtotal = sum(item.quantidade * item.preco_aplicado for item in self.carrinho)
        desconto = self.spin_desconto.value()
        total = max(0.0, subtotal - desconto)
        self.lbl_total.setText(f"<h2>R$ {total:.2f}</h2>")

    def _finalizar_venda(self):
        if not self.carrinho:
            QMessageBox.warning(self, "Aviso", "Carrinho vazio!")
            return

        cliente_obj = self.combo_clientes.currentData()
        cliente_id = cliente_obj["id"] if cliente_obj else None

        bandeira = self.combo_bandeira.currentText()
        if bandeira.startswith("Nenhum"):
            bandeira = None

        subtotal = sum(item.quantidade * item.preco_aplicado for item in self.carrinho)
        desconto = self.spin_desconto.value()
        total_final = max(0.0, subtotal - desconto)

        venda_dto = VendaDTO(
            cliente_id=cliente_id,
            forma_pagamento=self.combo_pagamento.currentText(),
            bandeira_cartao=bandeira,
            desconto=desconto,
            valor_total=total_final,
            itens=self.carrinho
        )

        try:
            res = self.venda_service.processar_venda(venda_dto)
            QMessageBox.information(self, "Venda Realizada", f"Venda #{res['venda_id']} de R$ {total_final:.2f} concluída com sucesso!")
            self.carrinho.clear()
            self.spin_desconto.setValue(0.0)
            self._atualizar_tabela_carrinho()
            self._atualizar_totais()
            self.carregar_produtos() # Recarrega estoque atualizado
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Finalizar Venda", str(e))