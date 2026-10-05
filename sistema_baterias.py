import os
import sqlite3
from datetime import datetime, timedelta

# ==========================================
# 1. CONEXÃO E CRIAÇÃO DO BANCO DE DADOS
# ==========================================

def conectar_bd():
    """Conecta ao SQLite e garante a criação das tabelas necessárias."""
    conn = sqlite3.connect("loja_baterias.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baterias'")
    tabela_existe = cursor.fetchone()

    if not tabela_existe:
        if os.path.exists("banco.sql"):
            with open("banco.sql", "r", encoding="utf-8") as f:
                script_sql = f.read()
                conn.executescript(script_sql)
            print("\n[SISTEMA] Banco de dados criado e populado a partir de 'banco.sql'!")
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS baterias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT, modelo TEXT, amperagem INTEGER, cca INTEGER,
                    voltagem INTEGER, aplicacao TEXT, garantia_meses INTEGER,
                    quantidade INTEGER, preco_custo REAL, preco_venda REAL,
                    preco_minimo REAL, valor_carcaca REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bateria_id INTEGER, cliente_cpf TEXT, numero_serie TEXT,
                    data_venda TEXT, com_troca INTEGER, valor_pago REAL,
                    forma_pagamento TEXT, garantia_ate TEXT
                )
            ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trocas_garantia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            bateria_id INTEGER,
            numero_serie_defeito TEXT,
            defeito_relatado TEXT,
            data_troca TEXT,
            status TEXT DEFAULT 'Defeituosa (Aguardando Troca/Fábrica)',
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (bateria_id) REFERENCES baterias(id)
        )
    ''')

    conn.commit()
    return conn

# ==========================================
# 2. FUNÇÕES AUXILIARES
# ==========================================

def buscar_bateria(termo):
    """Busca baterias no banco por ID (numérico) ou por Nome/Marca/Modelo (texto)."""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    termo = termo.strip()
    if termo.isdigit():
        cursor.execute("""
            SELECT id, marca, modelo, amperagem, cca, quantidade, preco_venda, preco_minimo, valor_carcaca, garantia_meses 
            FROM baterias WHERE id = ?
        """, (int(termo),))
    else:
        cursor.execute("""
            SELECT id, marca, modelo, amperagem, cca, quantidade, preco_venda, preco_minimo, valor_carcaca, garantia_meses 
            FROM baterias 
            WHERE marca LIKE ? OR modelo LIKE ? OR (marca || ' ' || modelo) LIKE ?
        """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
        
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def selecionar_bateria_da_busca(termo):
    """Auxilia o usuário a escolher uma única bateria a partir do termo pesquisado."""
    baterias = buscar_bateria(termo)
    
    if not baterias:
        print("[ERRO] Nenhuma bateria encontrada com o termo informado.")
        return None
        
    if len(baterias) == 1:
        return baterias[0]
        
    print("\nForam encontradas múltiplas baterias. Escolha uma abaixo:")
    print(f"{'ID':<4} | {'Marca/Modelo':<20} | {'Espec.':<10} | {'Estoque':<8} | {'Preço Tabela':<12}")
    print("-" * 60)
    for b in baterias:
        id_b, marca, modelo, ah, cca, qtd, p_venda = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
        print(f"{id_b:<4} | {marca + ' ' + modelo:<20} | {ah}Ah/{cca}A | {qtd:<8} | R$ {p_venda:.2f}")
        
    try:
        id_escolhido = int(input("\nDigite o ID exato da bateria desejada: "))
        for b in baterias:
            if b[0] == id_escolhido:
                return b
        print("[ERRO] ID digitado não está entre as opções listadas.")
        return None
    except ValueError:
        print("[ERRO] ID inválido.")
        return None

# ==========================================
# 3. MÓDULOS DE REGRAS DE NEGÓCIO
# ==========================================

def cadastrar_bateria():
    """Cadastra um NOVO modelo de bateria no catálogo."""
    print("\n--- CADASTRO DE NOVO MODELO DE BATERIA ---")
    try:
        marca = input("Marca (Ex: Moura, Heliar): ").strip()
        modelo = input("Modelo (Ex: M60AD): ").strip()
        amperagem = int(input("Amperagem (Ah) (Ex: 60): "))
        cca = int(input("CCA / Corrente de Partida (Ex: 450): "))
        voltagem = int(input("Voltagem (V) (Ex: 12): "))
        aplicacao = input("Aplicações (Ex: Passeio, Moto, Caminhão): ").strip()
        garantia_meses = int(input("Tempo de Garantia (em meses): "))
        quantidade = int(input("Quantidade Inicial em Estoque: "))
        
        print("\n-- Precificação --")
        preco_custo = float(input("Preço de Custo (R$): "))
        preco_venda = float(input("Preço Tabela de Venda (R$): "))
        preco_minimo = float(input("Preço Mínimo / Piso Promocional (R$): "))
        valor_carcaca = float(input("Valor do Desconto da Carcaça Usada (R$): "))

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO baterias 
            (marca, modelo, amperagem, cca, voltagem, aplicacao, garantia_meses, quantidade, preco_custo, preco_venda, preco_minimo, valor_carcaca)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (marca, modelo, amperagem, cca, voltagem, aplicacao, garantia_meses, quantidade, preco_custo, preco_venda, preco_minimo, valor_carcaca))
        
        conn.commit()
        conn.close()
        print("\n[SUCESSO] Novo modelo cadastrado com sucesso!")
    except ValueError:
        print("\n[ERRO] Entrada inválida! Verifique os valores numéricos digitados.")

def repor_estoque():
    """Adiciona quantidade de unidades a uma bateria JÁ CADASTRADA."""
    print("\n--- REPOSIÇÃO DE ESTOQUE (ADICIONAR UNIDADES) ---")
    termo = input("Digite o ID ou Nome/Marca/Modelo da bateria para reposição: ")
    bat = selecionar_bateria_da_busca(termo)
    
    if not bat:
        return

    id_bat, marca, modelo, qtd_atual = bat[0], bat[1], bat[2], bat[5]
    print(f"\nItem Selecionado: {marca} {modelo} | Estoque Atual: {qtd_atual} unidades")
    
    try:
        qtd_add = int(input("Quantidade de novas baterias a ADICIONAR ao estoque: "))
        if qtd_add <= 0:
            print("[ERRO] A quantidade a ser adicionada deve ser maior que zero.")
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("UPDATE baterias SET quantidade = quantidade + ? WHERE id = ?", (qtd_add, id_bat))
        conn.commit()
        conn.close()
        
        print(f"\n[SUCESSO] Estoque atualizado! Novo total: {qtd_atual + qtd_add} unidades.")
    except ValueError:
        print("[ERRO] Quantidade inválida.")

def listar_estoque():
    print("\n--- CONSULTA DE ESTOQUE E PREÇOS ---")
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, marca, modelo, amperagem, cca, aplicacao, quantidade, preco_venda, preco_minimo, valor_carcaca FROM baterias")
    baterias = cursor.fetchall()
    conn.close()

    if not baterias:
        print("Nenhuma bateria encontrada no cadastro.")
        return

    print(f"{'ID':<3} | {'Marca/Modelo':<18} | {'Espec.':<10} | {'Aplicação':<25} | {'Qtd':<8} | {'Tabela':<9} | {'Mínimo':<9} | {'Carcaça':<8}")
    print("-" * 103)
    for b in baterias:
        id_bat, marca, modelo, ah, cca, aplicacao, qtd, p_venda, p_min, v_carcaca = b
        nome = f"{marca} {modelo}"
        espec = f"{ah}Ah/{cca}A"
        
        alerta = " (BAIXO!)" if qtd <= 2 else ""
        print(f"{id_bat:<3} | {nome:<18} | {espec:<10} | {aplicacao[:25]:<25} | {str(qtd) + alerta:<8} | R$ {p_venda:<6.2f} | R$ {p_min:<6.2f} | R$ {v_carcaca:<6.2f}")

def atualizar_precificacao():
    listar_estoque()
    print("\n--- ATUALIZAÇÃO DE PRECIFICAÇÃO E PROMOÇÕES ---")
    termo = input("Informe o ID ou Nome da bateria que deseja alterar os preços: ")
    bat = selecionar_bateria_da_busca(termo)
    
    if not bat:
        return

    bateria_id, marca, modelo, p_venda, p_min, v_carcaca = bat[0], bat[1], bat[2], bat[6], bat[7], bat[8]

    try:
        print(f"\nEditando Preços de: {marca} {modelo}")
        novo_venda = float(input(f"Novo Preço Tabela (Atual: R$ {p_venda:.2f}): "))
        novo_minimo = float(input(f"Novo Preço Mínimo/Promocional (Atual: R$ {p_min:.2f}): "))
        novo_carcaca = float(input(f"Novo Valor de Desconto Carcaça (Atual: R$ {v_carcaca:.2f}): "))

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE baterias 
            SET preco_venda = ?, preco_minimo = ?, valor_carcaca = ?
            WHERE id = ?
        ''', (novo_venda, novo_minimo, novo_carcaca, bateria_id))
        
        conn.commit()
        conn.close()
        print("\n[SUCESSO] Preços atualizados com sucesso!")
    except ValueError:
        print("[ERRO] Valores digitados são inválidos.")

def realizar_venda():
    print("\n--- PONTO DE VENDA (PDV) ---")
    termo = input("Digite o ID ou o Nome/Marca/Modelo da bateria: ")
    bat = selecionar_bateria_da_busca(termo)
    
    if not bat:
        return
        
    id_bat, marca, modelo, ah, cca, qtd, p_venda, p_min, v_carcaca, garantia_meses = bat
    
    if qtd <= 0:
        print("\n[ERRO] Produto sem estoque disponível para venda!")
        return

    print(f"\nItem Selecionado: {marca} {modelo} ({ah}Ah)")
    print(f"Preço de Tabela: R$ {p_venda:.2f}")
    
    com_troca_in = input("O cliente entregará a bateria usada (troca/carcaça)? (S/N): ").strip().upper()
    com_troca = 1 if com_troca_in == 'S' else 0
    
    valor_base = p_venda
    if com_troca:
        valor_base -= v_carcaca
        print(f"-> Desconto de carcaça aplicado: -R$ {v_carcaca:.2f}")
    
    print(f"Valor sugerido com regras: R$ {valor_base:.2f}")
    
    try:
        valor_final = float(input("Informe o Preço Final de Venda negociado (R$): "))
    except ValueError:
        print("[ERRO] Valor digitado é inválido.")
        return
    
    limite_minimo = (p_min - v_carcaca) if com_troca else p_min
    if valor_final < limite_minimo:
        print(f"\n[BLOQUEADO] O valor negociado (R$ {valor_final:.2f}) é menor que o Preço Mínimo permitido (R$ {limite_minimo:.2f}). Venda não autorizada!")
        return

    cpf = input("CPF do Cliente (para Garantia): ").strip()
    num_serie = input("Número de Série gravado na bateria: ").strip()
    forma_pgto = input("Forma de Pagamento (PIX / Cartão / Dinheiro): ").strip()
    
    data_hoje = datetime.now()
    data_venda_str = data_hoje.strftime("%Y-%m-%d %H:%M:%S")
    
    data_garantia = data_hoje + timedelta(days=garantia_meses * 30)
    garantia_str = data_garantia.strftime("%Y-%m-%d")

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vendas (bateria_id, cliente_cpf, numero_serie, data_venda, com_troca, valor_pago, forma_pagamento, garantia_ate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_bat, cpf, num_serie, data_venda_str, com_troca, valor_final, forma_pgto, garantia_str))
    
    cursor.execute("UPDATE baterias SET quantidade = quantidade - 1 WHERE id = ?", (id_bat,))
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*40)
    print("      COMPROVANTE DE VENDA & GARANTIA      ")
    print("="*40)
    print(f"Produto: {marca} {modelo}")
    print(f"Nº de Série: {num_serie}")
    print(f"Cliente (CPF): {cpf}")
    print(f"Valor Pago: R$ {valor_final:.2f} ({forma_pgto})")
    print(f"Garantia Válida até: {data_garantia.strftime('%d/%m/%Y')}")
    print("="*40)

def consultar_vendas():
    """Consulta e exibe o histórico detalhado de vendas registradas."""
    print("\n--- CONSULTA DE VENDAS ---")
    print("[1] Listar todas as vendas")
    print("[2] Buscar por CPF do Cliente")
    print("[3] Buscar por Número de Série da Bateria")
    
    opcao = input("Escolha o tipo de consulta: ").strip()
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    query_base = '''
        SELECT v.id, b.marca, b.modelo, v.cliente_cpf, v.numero_serie, 
               v.data_venda, v.valor_pago, v.forma_pagamento, v.com_troca
        FROM vendas v
        JOIN baterias b ON v.bateria_id = b.id
    '''
    
    if opcao == '1':
        cursor.execute(query_base + " ORDER BY v.data_venda DESC")
    elif opcao == '2':
        cpf = input("Digite o CPF do cliente: ").strip()
        cursor.execute(query_base + " WHERE v.cliente_cpf = ? ORDER BY v.data_venda DESC", (cpf,))
    elif opcao == '3':
        serie = input("Digite o Nº de Série: ").strip()
        cursor.execute(query_base + " WHERE v.numero_serie = ? ORDER BY v.data_venda DESC", (serie,))
    else:
        print("[ERRO] Opção de busca inválida.")
        conn.close()
        return

    vendas = cursor.fetchall()
    conn.close()

    if not vendas:
        print("\n[INFO] Nenhuma venda encontrada para os critérios informados.")
        return

    print("\n" + "="*95)
    print(f"{'ID':<4} | {'Produto':<18} | {'CPF Cliente':<14} | {'Nº Série':<14} | {'Data':<10} | {'Valor':<9} | {'Pgto':<10}")
    print("-" * 95)
    for v in vendas:
        v_id, marca, modelo, cpf, serie, data_v, valor, pgto, troca = v
        prod = f"{marca} {modelo}"
        data_f = data_v[:10]
        print(f"{v_id:<4} | {prod:<18} | {cpf:<14} | {serie:<14} | {data_f:<10} | R$ {valor:<6.2f} | {pgto:<10}")
    print("="*95)

def consultar_garantia():
    print("\n--- CONSULTA DE GARANTIA DO CLIENTE ---")
    busca = input("Digite o CPF do cliente ou o Nº de Série da bateria: ").strip()
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, b.marca, b.modelo, v.numero_serie, v.cliente_cpf, v.data_venda, v.garantia_ate 
        FROM vendas v
        JOIN baterias b ON v.bateria_id = b.id
        WHERE v.cliente_cpf = ? OR v.numero_serie = ?
    ''', (busca, busca))
    
    vendas = cursor.fetchall()
    conn.close()

    if not vendas:
        print("[INFO] Nenhuma venda localizada com o dado informado.")
        return

    hoje = datetime.now().date()

    print("\nHistórico de Garantia:")
    for v in vendas:
        v_id, marca, modelo, num_serie, cpf, d_venda, g_ate = v
        dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
        
        status = "DENTRO DA GARANTIA" if hoje <= dt_garantia else "EXPIRADA"
        
        print("-" * 50)
        print(f"Registro: #{v_id} | Produto: {marca} {modelo}")
        print(f"Nº Série: {num_serie} | CPF: {cpf}")
        print(f"Data da Venda: {d_venda[:10]}")
        print(f"Garantia Até: {dt_garantia.strftime('%d/%m/%Y')} -> STATUS: [{status}]")

def processar_troca_garantia():
    """Gerencia a devolução de bateria defeituosa e substituição por uma nova."""
    print("\n--- TROCA DE BATERIA DEFEITUOSA (GARANTIA) ---")
    busca = input("Digite o CPF do Cliente ou Nº de Série da bateria com defeito: ").strip()
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, v.bateria_id, b.marca, b.modelo, v.numero_serie, v.cliente_cpf, v.garantia_ate 
        FROM vendas v
        JOIN baterias b ON v.bateria_id = b.id
        WHERE v.cliente_cpf = ? OR v.numero_serie = ?
    ''', (busca, busca))
    vendas = cursor.fetchall()
    
    if not vendas:
        print("[ERRO] Nenhuma venda localizada para os dados informados.")
        conn.close()
        return

    print("\nSelecione qual item está apresentando defeito:")
    for idx, v in enumerate(vendas, 1):
        v_id, bat_id, marca, modelo, num_serie, cpf, g_ate = v
        dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
        status_g = "DENTRO DA GARANTIA" if datetime.now().date() <= dt_garantia else "EXPIRADA"
        print(f"[{idx}] Venda #{v_id} | {marca} {modelo} | Nº Série: {num_serie} | Vencimento Garantia: {dt_garantia.strftime('%d/%m/%Y')} [{status_g}]")

    try:
        op = int(input("\nOpção correspondente: ")) - 1
        venda_sel = vendas[op]
    except (ValueError, IndexError):
        print("[ERRO] Seleção inválida.")
        conn.close()
        return

    v_id, bat_id, marca, modelo, num_serie_antigo, cpf, g_ate = venda_sel
    dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
    
    if datetime.now().date() > dt_garantia:
        print("\n[ALERTA] A garantia desta bateria está EXPIRADA!")
        confirmar = input("Deseja realizar a troca em caráter de exceção/cortesia? (S/N): ").strip().upper()
        if confirmar != 'S':
            conn.close()
            return

    cursor.execute("SELECT quantidade FROM baterias WHERE id = ?", (bat_id,))
    res_estoque = cursor.fetchone()
    
    if not res_estoque or res_estoque[0] <= 0:
        print(f"\n[ERRO] Não há baterias novas de reposição ({marca} {modelo}) em estoque!")
        conn.close()
        return

    defeito = input("Informe o defeito constatado (Ex: Placa em curto, Vazamento, Não segura carga): ").strip()
    num_serie_novo = input("Digite o Nº de Série da NOVA bateria que será entregue: ").strip()

    data_hoje_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO trocas_garantia (venda_id, bateria_id, numero_serie_defeito, defeito_relatado, data_troca)
        VALUES (?, ?, ?, ?, ?)
    ''', (v_id, bat_id, num_serie_antigo, defeito, data_hoje_str))

    cursor.execute("UPDATE vendas SET numero_serie = ? WHERE id = ?", (num_serie_novo, v_id))
    cursor.execute("UPDATE baterias SET quantidade = quantidade - 1 WHERE id = ?", (bat_id,))

    conn.commit()
    conn.close()

    print("\n" + "="*50)
    print("   TROCA EM GARANTIA REALIZADA COM SUCESSO!   ")
    print("="*50)
    print(f"Bateria Devolvida (Ruim): {marca} {modelo} | Série: {num_serie_antigo}")
    print(f"Defeito Anotado: {defeito}")
    print(f"Nova Bateria Entregue: Série {num_serie_novo}")
    print("="*50)

def consultar_total_baterias_ruins():
    """Calcula e exibe automaticamente o total de baterias ruins (trocas + garantia)."""
    conn = conectar_bd()
    cursor = conn.cursor()

    # 1. Carcaças recolhidas de vendas com troca
    cursor.execute("SELECT COALESCE(SUM(com_troca), 0) FROM vendas")
    carcacas_troca = cursor.fetchone()[0]

    # 2. Baterias devolvidas por garantia/defeito
    cursor.execute("SELECT COUNT(*) FROM trocas_garantia")
    garantias_defeito = cursor.fetchone()[0]

    conn.close()

    total_ruins = carcacas_troca + garantias_defeito

    print("\n" + "="*50)
    print("    CONTROLE AUTOMÁTICO DE BATERIAS RUINS   ")
    print("="*50)
    print(f" Carcaças de Troca (Entrada em Vendas) : {carcacas_troca} unidades")
    print(f" Devoluções por Garantia (Com Defeito) : {garantias_defeito} unidades")
    print("-" * 50)
    print(f" TOTAL DE BATERIAS RUINS NO ESTOQUE    : {total_ruins} unidades")
    print("="*50)
    return total_ruins

def relatorio_gerencial():
    print("\n--- RELATÓRIOS GERENCIAIS ---")
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Métricas de vendas
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_pago), 0), COALESCE(SUM(com_troca), 0) FROM vendas")
    res_vendas = cursor.fetchone()
    total_vendas = res_vendas[0] or 0
    faturamento = res_vendas[1] or 0.0
    total_carcacas = res_vendas[2] or 0

    # Métricas de defeitos / trocas
    cursor.execute('''
        SELECT t.id, b.marca, b.modelo, t.numero_serie_defeito, t.defeito_relatado, t.data_troca, t.status
        FROM trocas_garantia t
        JOIN baterias b ON t.bateria_id = b.id
    ''')
    defeitos = cursor.fetchall()
    conn.close()

    total_garantia = len(defeitos)
    total_baterias_ruins = total_carcacas + total_garantia

    print("=" * 55)
    print(f" Total de Baterias Vendidas          : {total_vendas}")
    print(f" Faturamento Total Acumulado         : R$ {faturamento:.2f}")
    print(f" Carcaças Recolhidas (Troca em Venda): {total_carcacas} unidades")
    print(f" Baterias Devolvidas por Garantia    : {total_garantia} unidades")
    print("-" * 55)
    print(f" TOTAL GERAL DE BATERIAS RUINS       : {total_baterias_ruins} unidades")
    print("=" * 55)

    if defeitos:
        print("\n--- DETALHAMENTO DE BATERIAS RUINS / DEVOLVIDAS EM GARANTIA ---")
        print(f"{'ID':<3} | {'Produto':<18} | {'Nº Série Defeito':<18} | {'Defeito Relatado':<25}")
        print("-" * 70)
        for d in defeitos:
            d_id, marca, modelo, serie_def, def_rel, data_t, status = d
            prod = f"{marca} {modelo}"
            print(f"{d_id:<3} | {prod:<18} | {serie_def:<18} | {def_rel[:25]:<25}")

# ==========================================
# 4. MENU PRINCIPAL
# ==========================================

def menu():
    conectar_bd()
    while True:
        print("\n" + "="*45)
        print("   SISTEMA DE GESTÃO - LOJA DE BATERIAS   ")
        print("="*45)
        print("[1] Cadastrar Novo Modelo de Bateria")
        print("[2] Adicionar Estoque (Reposição de Unidades)")
        print("[3] Consultar Estoque e Preços")
        print("[4] Ajustar Precificação / Preço Mínimo")
        print("[5] Realizar Venda (PDV - Busca por ID ou Nome)")
        print("[6] Consultar Vendas Realizadas")
        print("[7] Consultar Garantia do Cliente")
        print("[8] Registrar Troca de Bateria Defeituosa (Garantia)")
        print("[9] Consultar Quantidade de Baterias Ruins")
        print("[10] Relatórios Gerenciais Completos")
        print("[0] Sair do Sistema")
        
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_bateria()
        elif opcao == '2':
            repor_estoque()
        elif opcao == '3':
            listar_estoque()
        elif opcao == '4':
            atualizar_precificacao()
        elif opcao == '5':
            realizar_venda()
        elif opcao == '6':
            consultar_vendas()
        elif opcao == '7':
            consultar_garantia()
        elif opcao == '8':
            processar_troca_garantia()
        elif opcao == '9':
            consultar_total_baterias_ruins()
        elif opcao == '10':
            relatorio_gerencial()
        elif opcao == '0':
            print("\nEncerrando o sistema... Até logo!")
            break
        else:
            print("\n[ERRO] Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()