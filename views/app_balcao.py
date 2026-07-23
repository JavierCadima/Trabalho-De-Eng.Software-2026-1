import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

# Importações dos DTOs e Camadas de Serviço do Backend
from models.venda import VendaDTO, ItemVenda
from services.venda_service import VendaService
from services.garantia_service import GarantiaService
from services.relatorio_service import RelatorioService
from repositories.produto_repository import ProdutoRepository
from views.cadastro_produto_dialog import CadastroProdutoDialog


class PDVBalcaoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frente de Balcão - Auto Mecânica & Baterias")
        self.setGeometry(100, 100, 1080, 700)

        # Instâncias dos Serviços do Backend
        self.venda_service = VendaService()
        self.garantia_service = GarantiaService()
        self.relatorio_service = RelatorioService()
        self.produto_repo = ProdutoRepository()

        # Carrinho armazenado na memória da sessão da interface
        self.carrinho_itens = []

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()

        # =========================================================================
        # PAINEL ESQUERDO: CONTROLES DE ENTRADA, CADASTRO E PAGAMENTO
        # =========================================================================
        left_panel = QVBoxLayout()

        # --- Bloco 1: Lançamento de Itens ---
        left_panel.addWidget(QLabel("<b>Lançamento de Bateria / Item</b>"))

        self.input_prod_id = QLineEdit()
        self.input_prod_id.setPlaceholderText("ID do Produto (Ex: 1)")
        left_panel.addWidget(self.input_prod_id)

        self.input_serie = QLineEdit()
        self.input_serie.setPlaceholderText("Número de Série (Para Garantia)")
        left_panel.addWidget(self.input_serie)

        self.chk_sucata = QCheckBox("Cliente entregou a bateria antiga (Com Troca)")
        self.chk_sucata.setChecked(True)
        left_panel.addWidget(self.chk_sucata)

        btn_adicionar = QPushButton("Adicionar ao Carrinho [F2]")
        btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #1A365D; 
                color: white; 
                font-weight: bold; 
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2A4365; }
        """)
        btn_adicionar.clicked.connect(self._handle_adicionar_item)
        left_panel.addWidget(btn_adicionar)

        left_panel.addSpacing(10)

        # Botão rápido para cadastrar novos produtos
        btn_cadastrar_prod = QPushButton("➕ Cadastrar Nova Bateria")
        btn_cadastrar_prod.setStyleSheet("""
            QPushButton {
                background-color: #4A5568; 
                color: white; 
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #718096; }
        """)
        btn_cadastrar_prod.clicked.connect(self._abrir_cadastro_produto)
        left_panel.addWidget(btn_cadastrar_prod)

        left_panel.addSpacing(15)

        # --- Bloco 2: Pagamento e Condições de Cartão ---
        left_panel.addWidget(QLabel("<b>Forma de Pagamento & Condições</b>"))

        # Seleção da Forma de Pagamento
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
        self.combo_pagamento.currentTextChanged.connect(self._toggle_opcoes_cartao)
        left_panel.addWidget(self.combo_pagamento)

        # Seleção de Bandeira (Exibido para Crédito e Débito)
        self.lbl_bandeira = QLabel("Bandeira do Cartão:")
        left_panel.addWidget(self.lbl_bandeira)
        
        self.combo_bandeira = QComboBox()
        self.combo_bandeira.addItems(["Visa", "Mastercard", "Elo", "Hipercard", "Amex"])
        left_panel.addWidget(self.combo_bandeira)

        # Seleção de Parcelamento (Exibido apenas para Crédito - 1x até 12x)
        self.lbl_parcelas = QLabel("Parcelamento:")
        left_panel.addWidget(self.lbl_parcelas)
        
        self.combo_parcelas = QComboBox()
        for i in range(1, 13):
            self.combo_parcelas.addItem(f"{i}x à vista" if i == 1 else f"{i}x sem juros")
        left_panel.addWidget(self.combo_parcelas)

        # Atualiza a visibilidade inicial dos campos de cartão
        self._toggle_opcoes_cartao(self.combo_pagamento.currentText())

        left_panel.addSpacing(5)

        # Campo de Desconto
        self.input_desconto = QLineEdit()
        self.input_desconto.setPlaceholderText("Desconto Geral (R$)")
        self.input_desconto.setText("0.00")
        left_panel.addWidget(self.input_desconto)

        left_panel.addSpacing(10)

        # Botão Concluir Venda
        btn_finalizar = QPushButton("FINALIZAR VENDA [F10]")
        btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #2F855A; 
                color: white; 
                font-weight: bold; 
                font-size: 13px; 
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #38A169; }
        """)
        btn_finalizar.clicked.connect(self._handle_finalizar_venda)
        left_panel.addWidget(btn_finalizar)

        left_panel.addSpacing(15)

        # --- Bloco 3: Relatórios e Utilidades ---
        btn_relatorio = QPushButton("📄 Gerar Relatório Fechamento PDF")
        btn_relatorio.setStyleSheet("""
            QPushButton {
                background-color: #2B6CB0; 
                color: white; 
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3182CE; }
        """)
        btn_relatorio.clicked.connect(self._handle_gerar_relatorio)
        left_panel.addWidget(btn_relatorio)

        left_panel.addStretch()

        # =========================================================================
        # PAINEL DIREITO: TABELA DE ITENS NO CARRINHO E MOSTRADOR DE TOTAL
        # =========================================================================
        right_panel = QVBoxLayout()

        right_panel.addWidget(QLabel("<b>Itens da Venda Atual</b>"))

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["ID Prod.", "Descrição / Modelo", "Nº Série", "Com Troca?", "Preço Un."])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        right_panel.addWidget(self.tabela)

        # Display do Total da Compra
        self.lbl_total = QLabel("TOTAL: R$ 0,00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #2F855A; margin-top: 10px;")
        right_panel.addWidget(self.lbl_total)

        # Montagem do Layout Principal (Esquerda: 35% | Direita: 65%)
        main_layout.addLayout(left_panel, 35)
        main_layout.addLayout(right_panel, 65)
        central_widget.setLayout(main_layout)

    # =========================================================================
    # LÓGICA DE INTERFACE E EVENTOS
    # =========================================================================

    def _toggle_opcoes_cartao(self, forma_pagamento: str):
        """Habilita/desabilita dinamicamente os seletores de bandeira e parcelamento."""
        eh_credito = (forma_pagamento == "Cartão de Crédito")
        eh_debito = (forma_pagamento == "Cartão de Débito")

        # Exibe bandeira para crédito e débito
        self.lbl_bandeira.setVisible(eh_credito or eh_debito)
        self.combo_bandeira.setVisible(eh_credito or eh_debito)

        # Exibe parcelamento de 1x a 12x somente se for Crédito
        self.lbl_parcelas.setVisible(eh_credito)
        self.combo_parcelas.setVisible(eh_credito)

    def _abrir_cadastro_produto(self):
        """Abre a janela popup dialog para registrar um novo produto/bateria."""
        dialog = CadastroProdutoDialog(self)
        dialog.exec()

    def _handle_adicionar_item(self):
        """Consulta o backend, valida o estoque e adiciona o item ao carrinho local."""
        prod_id_str = self.input_prod_id.text().strip()
        numero_serie = self.input_serie.text().strip()
        entregou_sucata = self.chk_sucata.isChecked()

        if not prod_id_str:
            QMessageBox.warning(self, "Aviso", "Informe o ID do Produto para continuar.")
            return

        try:
            prod_id = int(prod_id_str)
            produto = self.produto_repo.buscar_por_id(prod_id)

            if not produto:
                QMessageBox.critical(self, "Erro", f"Produto com ID #{prod_id} não encontrado no cadastro!")
                return

            if produto["estoque_atual"] <= 0:
                QMessageBox.warning(self, "Estoque Insuficiente", f"A bateria '{produto['nome']}' está sem estoque disponível!")
                return

            # Seleciona a tabela de preço apropriada (com ou sem carcaça de sucata)
            preco_aplicado = produto["preco_com_troca"] if entregou_sucata else produto["preco_venda"]

            item_dto = ItemVenda(
                produto_id=prod_id,
                quantidade=1,
                numero_serie=numero_serie,
                entregou_sucata=entregou_sucata,
                preco_aplicado=preco_aplicado,
                categoria=produto["categoria"]
            )

            self.carrinho_itens.append({
                "item_dto": item_dto, 
                "nome_produto": produto["nome"]
            })

            self._atualizar_tabela()

            # Limpa os campos após adicionar com sucesso
            self.input_prod_id.clear()
            self.input_serie.clear()

        except ValueError:
            QMessageBox.warning(self, "Erro de Validação", "O ID do Produto deve ser um número inteiro.")

    def _atualizar_tabela(self):
        """Atualiza a QTableWidget e calcula o subtotal acumulado."""
        self.tabela.setRowCount(0)
        subtotal = 0.0

        for row, elem in enumerate(self.carrinho_itens):
            item: ItemVenda = elem["item_dto"]
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(item.produto_id)))
            self.tabela.setItem(row, 1, QTableWidgetItem(elem["nome_produto"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(item.numero_serie))
            self.tabela.setItem(row, 3, QTableWidgetItem("Sim" if item.entregou_sucata else "Não"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {item.preco_aplicado:.2f}"))

            subtotal += item.preco_aplicado

        self.lbl_total.setText(f"TOTAL: R$ {subtotal:.2f}")

    def _handle_finalizar_venda(self):
        """Envia o DTO completo para o VendaService processar no banco de dados."""
        if not self.carrinho_itens:
            QMessageBox.warning(self, "Carrinho Vazio", "Adicione ao menos uma bateria ao carrinho antes de finalizar.")
            return

        try:
            desconto = float(self.input_desconto.text().replace(",", ".") or 0.0)
            forma_pagamento = self.combo_pagamento.currentText()
            
            parcelas = 1
            bandeira = None

            if forma_pagamento == "Cartão de Crédito":
                parcelas = self.combo_parcelas.currentIndex() + 1
                bandeira = self.combo_bandeira.currentText()
            elif forma_pagamento == "Cartão de Débito":
                bandeira = self.combo_bandeira.currentText()

            itens_dto = [elem["item_dto"] for elem in self.carrinho_itens]

            venda_dto = VendaDTO(
                forma_pagamento=forma_pagamento,
                desconto=desconto,
                itens=itens_dto,
                parcelas=parcelas,
                bandeira_cartao=bandeira
            )

            # Processa a venda na camada de negócios
            resultado = self.venda_service.processar_venda(venda_dto)

            # Detalhamento visual da confirmação de venda
            info_detalhe = forma_pagamento
            if forma_pagamento == "Cartão de Crédito":
                val_parcela = resultado['total'] / parcelas
                info_detalhe += f" ({bandeira} - {parcelas}x de R$ {val_parcela:.2f})"
            elif forma_pagamento == "Cartão de Débito":
                info_detalhe += f" ({bandeira})"

            QMessageBox.information(
                self, 
                "Venda Realizada com Sucesso!", 
                f"✓ Venda #{resultado['venda_id']} processada no sistema!\n\n"
                f"• Pagamento: {info_detalhe}\n"
                f"• Valor Final Pago: R$ {resultado['total']:.2f}"
            )

            # Reseta a interface para a próxima venda
            self.carrinho_itens.clear()
            self.input_desconto.setText("0.00")
            self._atualizar_tabela()

        except Exception as e:
            QMessageBox.critical(self, "Erro no Processamento", f"Não foi possível concluir a venda: {str(e)}")

    def _handle_gerar_relatorio(self):
        """Dispara a geração do relatório gerencial em PDF e abre o arquivo nativamente."""
        try:
            caminho_pdf = self.relatorio_service.gerar_pdf_fechamento()
            caminho_abs = os.path.abspath(caminho_pdf)
            os.startfile(caminho_abs)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Gerar PDF", str(e))