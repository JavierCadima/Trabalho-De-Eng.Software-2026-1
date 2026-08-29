import os
import sys
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from database.connection import get_connection

APP_NAME = "AutoMecanicaBaterias"


def get_default_output_dir():
    if getattr(sys, "frozen", False):
        base_dir = Path(os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or Path.home() / "AppData" / "Local") / APP_NAME
    else:
        base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "relatorios"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


class RelatorioService:
    def __init__(self, pasta_saida=None):
        self.pasta_saida = pasta_saida or get_default_output_dir()
        Path(self.pasta_saida).mkdir(parents=True, exist_ok=True)

    def gerar_pdf_fechamento(self) -> str:
        """
        Consulta o banco de dados e gera o PDF de fechamento de caixa do dia,
        incluindo bandeiras e parcelas na tabela de vendas.
        """
        hoje = datetime.now().strftime("%Y-%m-%d")
        data_formatada = datetime.now().strftime("%d/%m/%Y - %H:%M")
        
        caminho_arquivo = os.path.join(self.pasta_saida, f"fechamento_{hoje}.pdf")

        # 1. Busca os dados no Banco de Dados
        dados_vendas, resumo_financeiro = self._buscar_vendas_do_dia(hoje)
        dados_sucatas = self._buscar_estoque_sucatas()

        # 2. Configuração do PDF
        doc = SimpleDocTemplate(
            caminho_arquivo,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'TituloStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=4
        )
        subtitulo_style = ParagraphStyle(
            'SubTituloStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor("#718096"),
            spaceAfter=15
        )
        secao_style = ParagraphStyle(
            'SecaoStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=12,
            spaceAfter=6
        )

        elements = []

        # Cabeçalho
        elements.append(Paragraph("<b>AUTO MECÂNICA & BATERIAS</b>", titulo_style))
        elements.append(Paragraph(f"Relatório de Fechamento de Caixa • Emissão: {data_formatada}", subtitulo_style))
        elements.append(Spacer(1, 5))

        # --- SEÇÃO 1: RESUMO FINANCEIRO ---
        elements.append(Paragraph("Resumo do Dia", secao_style))
        
        tabela_resumo_data = [
            ["Qtd. Vendas", "Subtotal Bruto", "Total Descontos", "Total Líquido"],
            [
                str(resumo_financeiro['qtd_vendas']),
                f"R$ {resumo_financeiro['subtotal']:.2f}",
                f"R$ {resumo_financeiro['desconto']:.2f}",
                f"R$ {resumo_financeiro['total']:.2f}"
            ]
        ]
        
        tabela_resumo = Table(tabela_resumo_data, colWidths=[120, 140, 140, 140])
        tabela_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2D3748")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor("#2F855A")),
        ]))
        elements.append(tabela_resumo)
        elements.append(Spacer(1, 10))

        # --- SEÇÃO 2: LOGÍSTICA REVERSA (ESTOQUE DE SUCATAS) ---
        elements.append(Paragraph("Estoque de Sucatas Recolhidas (Carcaças)", secao_style))
        
        tabela_sucatas_data = [["Categoria de Bateria", "Quantidade Acumulada"]]
        for item in dados_sucatas:
            tabela_sucatas_data.append([item['categoria'], f"{item['quantidade']} un"])

        if len(tabela_sucatas_data) == 1:
            tabela_sucatas_data.append(["Nenhuma sucata registrada", "0 un"])

        tabela_sucatas = Table(tabela_sucatas_data, colWidths=[300, 240])
        tabela_sucatas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(tabela_sucatas)
        elements.append(Spacer(1, 10))

        # --- SEÇÃO 3: LISTA DE VENDAS (COM BANDEIRA E PARCELAS) ---
        elements.append(Paragraph("Detalhamento das Vendas", secao_style))
        
        # Ajustamos a largura da coluna de Pagamento para 180 para caber as bandeiras/parcelas
        tabela_vendas_data = [["ID", "Horário", "Forma de Pagamento / Detalhes", "Desconto", "Total"]]
        
        for v in dados_vendas:
            detalhe_pagamento = v['forma_pagamento']
            
            # Formatação especial para cartões
            if v['forma_pagamento'] == "Cartão de Crédito":
                bandeira_str = f" - {v['bandeira']}" if v['bandeira'] else ""
                parcelas_str = f" ({v['parcelas']}x)" if v['parcelas'] > 1 else " (1x)"
                detalhe_pagamento = f"Crédito{bandeira_str}{parcelas_str}"
                
            elif v['forma_pagamento'] == "Cartão de Débito":
                bandeira_str = f" - {v['bandeira']}" if v['bandeira'] else ""
                detalhe_pagamento = f"Débito{bandeira_str}"

            tabela_vendas_data.append([
                f"#{v['id']}",
                v['horario'],
                detalhe_pagamento,
                f"R$ {v['desconto']:.2f}",
                f"R$ {v['valor_total']:.2f}"
            ])

        if len(tabela_vendas_data) == 1:
            tabela_vendas_data.append(["-", "Sem vendas hoje", "-", "-", "-"])

        tabela_vendas = Table(tabela_vendas_data, colWidths=[45, 75, 200, 110, 110])
        tabela_vendas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Alinha o texto do pagamento à esquerda para melhor leitura
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(tabela_vendas)

        # Build do PDF
        doc.build(elements)
        return caminho_arquivo

    def gerar_pdf_vendas(self, data_inicio=None, data_fim=None) -> str:
        """
        Exporta as vendas registradas em PDF.
        Se não passar data_inicio/data_fim, exporta todas as vendas.
        """
        data_inicio_str = data_inicio or "todas"
        data_fim_str = data_fim or ""
        nome_arquivo = f"vendas_{data_inicio_str}{('_a_' + data_fim_str) if data_fim else ''}.pdf"
        caminho_arquivo = os.path.join(self.pasta_saida, nome_arquivo)

        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT v.id, c.nome AS cliente, v.data_venda, v.forma_pagamento,
                   v.bandeira_cartao, v.parcelas, v.desconto, v.valor_total
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
        """
        conditions = []
        params = []
        if data_inicio:
            conditions.append("DATE(v.data_venda) >= ?")
            params.append(data_inicio)
        if data_fim:
            conditions.append("DATE(v.data_venda) <= ?")
            params.append(data_fim)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY v.data_venda DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'TituloStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=4
        )
        subtitulo_style = ParagraphStyle(
            'SubTituloStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor("#718096"),
            spaceAfter=15
        )
        secao_style = ParagraphStyle(
            'SecaoStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=12,
            spaceAfter=6
        )

        doc = SimpleDocTemplate(
            caminho_arquivo,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
        elements.append(Paragraph("<b>Relatório de Vendas</b>", titulo_style))
        if data_inicio or data_fim:
            periodo = f"Período: {data_inicio or 'início'} até {data_fim or 'fim'}"
            elements.append(Paragraph(periodo, subtitulo_style))
        elements.append(Spacer(1, 10))

        tabela_dados = [["ID", "Data/Hora", "Cliente", "Pagamento", "Desconto", "Total"]]
        for row in rows:
            forma_pagamento = row['forma_pagamento']
            if forma_pagamento == "Cartão de Crédito":
                bandeira = f" - {row['bandeira_cartao']}" if row['bandeira_cartao'] else ""
                forma_pagamento = f"Crédito{bandeira} ({row['parcelas']}x)"
            elif forma_pagamento == "Cartão de Débito":
                bandeira = f" - {row['bandeira_cartao']}" if row['bandeira_cartao'] else ""
                forma_pagamento = f"Débito{bandeira}"

            tabela_dados.append([
                str(row['id']),
                row['data_venda'],
                row['cliente'] or "Avulso",
                forma_pagamento,
                f"R$ {row['desconto']:.2f}",
                f"R$ {row['valor_total']:.2f}"
            ])

        tabela = Table(tabela_dados, colWidths=[40, 110, 140, 170, 80, 80])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(tabela)
        doc.build(elements)
        return caminho_arquivo

    # ==================== CONSULTA SQL ATUALIZADA ====================

    def _buscar_vendas_do_dia(self, data_hoje: str):
        conn = get_connection()
        cursor = conn.cursor()

        # Adicionados os campos bandeira_cartao e parcelas no SELECT
        cursor.execute("""
            SELECT id, strftime('%H:%M', data_venda) as horario, 
                   forma_pagamento, bandeira_cartao, parcelas, 
                   desconto, valor_total
            FROM vendas
            WHERE DATE(data_venda) = ?
            ORDER BY id DESC
        """, (data_hoje,))

        rows = cursor.fetchall()
        conn.close()

        vendas = []
        subtotal = 0.0
        total_desconto = 0.0
        total_liquido = 0.0

        for row in rows:
            desconto = row["desconto"] or 0.0
            valor_total = row["valor_total"] or 0.0

            vendas.append({
                "id": row["id"],
                "horario": row["horario"],
                "forma_pagamento": row["forma_pagamento"],
                "bandeira": row["bandeira_cartao"],
                "parcelas": row["parcelas"] or 1,
                "desconto": desconto,
                "valor_total": valor_total
            })

            total_desconto += desconto
            total_liquido += valor_total
            subtotal += (valor_total + desconto)

        resumo = {
            "qtd_vendas": len(vendas),
            "subtotal": subtotal,
            "desconto": total_desconto,
            "total": total_liquido
        }

        return vendas, resumo

    def _buscar_estoque_sucatas(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT categoria, quantidade 
            FROM sucatas_estoque
            ORDER BY quantidade DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [{"categoria": row["categoria"], "quantidade": row["quantidade"]} for row in rows]