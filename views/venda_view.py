from datetime import datetime, timedelta
from models.venda import Venda
from models.cliente import Cliente
from models.sessao import SessaoSistema
from repositories.bateria_repository import BateriaRepository
from repositories.venda_repository import VendaRepository
from repositories.cliente_repository import ClienteRepository
from repositories.funcionario_repository import FuncionarioRepository
from views.bateria_view import selecionar_bateria_da_busca

def realizar_venda():
    """Ponto de Venda (PDV) com suporte a Carrinho de Compras e Autorização de Fiscal."""
    if not SessaoSistema.tem_permissao("venda_realizar"):
        print("\n[ACESSO NEGADO] Seu cargo não possui permissão para realizar vendas.")
        return

    print("\n" + "=" * 50)
    print("        PONTO DE VENDA (PDV) - CARRINHO         ")
    print("=" * 50)

    carrinho = []

    while True:
        print("\n--- ADICIONAR ITEM AO CARRINHO ---")
        termo = input("Digite o ID ou Nome/Marca/Modelo da bateria (ou '0' para finalizar): ").strip()
        if termo == '0':
            if not carrinho:
                print("[INFO] Carrinho vazio. Venda cancelada.")
                return
            break

        bat = selecionar_bateria_da_busca(termo)
        if not bat:
            continue

        id_bat, marca, modelo, ah, cca, qtd_estoque, p_venda, p_min, v_carcaca, garantia_meses = bat

        # Verificar se o item já está no carrinho e subtrair do estoque disponível
        qtd_ja_no_carrinho = sum(1 for item in carrinho if item['id_bat'] == id_bat)
        if (qtd_estoque - qtd_ja_no_carrinho) <= 0:
            print(f"\n[ERRO] Produto sem estoque disponível adicional para venda! (Disponível: {qtd_estoque - qtd_ja_no_carrinho})")
            continue

        print(f"\nItem Selecionado: {marca} {modelo} ({ah}Ah)")
        print(f"Preço de Tabela: R$ {p_venda:.2f}")

        com_troca_in = input("O cliente entregará a bateria usada (troca/carcaça)? (S/N): ").strip().upper()
        com_troca = 1 if com_troca_in == 'S' else 0

        valor_base = p_venda - (v_carcaca if com_troca else 0)
        if com_troca:
            print(f"-> Desconto de carcaça aplicado: -R$ {v_carcaca:.2f}")
        print(f"Valor sugerido com regras: R$ {valor_base:.2f}")

        try:
            valor_final = float(input("Informe o Preço Final de Venda negociado (R$): "))
        except ValueError:
            print("[ERRO] Valor digitado é inválido.")
            continue

        limite_minimo = (p_min - v_carcaca) if com_troca else p_min
        if valor_final < limite_minimo:
            print(f"\n[BLOQUEADO] O valor negociado (R$ {valor_final:.2f}) é menor que o Preço Mínimo permitido (R$ {limite_minimo:.2f}).")
            continue

        num_serie = input("Número de Série gravado nesta bateria: ").strip()
        if not num_serie:
            print("[ERRO] Número de série é obrigatório para controle de garantia.")
            continue

        item_carrinho = {
            'id_bat': id_bat,
            'marca': marca,
            'modelo': modelo,
            'ah': ah,
            'valor_final': valor_final,
            'com_troca': com_troca,
            'num_serie': num_serie,
            'garantia_meses': garantia_meses
        }
        carrinho.append(item_carrinho)
        print(f"\n[OK] {marca} {modelo} adicionado ao carrinho com sucesso!")

        # Menu intermediário do carrinho
        print("\n" + "-" * 45)
        print(f" ITENS ATUAIS NO CARRINHO: {len(carrinho)}")
        for idx, it in enumerate(carrinho, 1):
            print(f"  [{idx}] {it['marca']} {it['modelo']} (Série: {it['num_serie']}) - R$ {it['valor_final']:.2f}")
        total_parcial = sum(it['valor_final'] for it in carrinho)
        print(f" TOTAL PARCIAL: R$ {total_parcial:.2f}")
        print("-" * 45)

        print("[1] Adicionar Outra Bateria")
        print("[2] Retirar Produto do Carrinho (Exige Fiscal/Gerente)")
        print("[3] Concluir e Fechar Venda")
        print("[0] Cancelar Toda a Venda")

        acao = input("\nEscolha a ação: ").strip()
        if acao == '1':
            continue
        elif acao == '2':
            _processar_remocao_item_carrinho(carrinho)
            if not carrinho:
                print("\n[INFO] O carrinho ficou vazio. Voltando ao início do PDV...")
        elif acao == '3':
            break
        elif acao == '0':
            print("\n[INFO] Venda cancelada pelo operador.")
            return

    if not carrinho:
        print("[INFO] Nenhum item no carrinho.")
        return

    # --- IDENTIFICAÇÃO E DADOS DO CLIENTE ---
    print("\n--- DADOS DO CLIENTE PARA CADASTRO E GARANTIA ---")
    cpf = input("CPF do Cliente: ").strip()
    if not cpf:
        print("[ERRO] CPF é obrigatório.")
        return

    cliente_existente = ClienteRepository.buscar_por_cpf(cpf)
    pode_ver_dados = SessaoSistema.tem_permissao("cliente_ver_dados")

    if cliente_existente:
        end_display = cliente_existente.endereco if pode_ver_dados else "[RESTRITO - REQUER FISCAL/GERENTE]"
        print(f"\n[CLIENTE LOCALIZADO]")
        print(f"Nome     : {cliente_existente.nome}")
        print(f"Endereço : {end_display}")
        print(f"Telefone : {cliente_existente.telefone}")
        nome_cliente = cliente_existente.nome
        endereco_cliente = cliente_existente.endereco
    else:
        if not SessaoSistema.tem_permissao("cliente_cadastrar"):
            print("\n[ACESSO NEGADO] Você não tem permissão para cadastrar um novo cliente.")
            print("A venda foi cancelada.")
            return

        print("\n[NOVO CLIENTE - CADASTRAR]")
        nome_cliente = input("Nome Completo do Cliente: ").strip()
        endereco_cliente = input("Endereço Completo (Rua, Número, Bairro, Cidade): ").strip()
        telefone_cliente = input("Telefone para Contato: ").strip()
        novo_cli = Cliente(cpf=cpf, nome=nome_cliente, endereco=endereco_cliente, telefone=telefone_cliente)
        ClienteRepository.salvar(novo_cli)
        print("[OK] Cliente cadastrado com sucesso!")

    forma_pgto = input("\nForma de Pagamento (PIX / Cartão / Dinheiro): ").strip()
    data_hoje = datetime.now()
    data_venda_str = data_hoje.strftime("%Y-%m-%d %H:%M:%S")

    # --- PERSISTÊNCIA DOS ITENS DA VENDA ---
    print("\n" + "=" * 55)
    print("           COMPROVANTE DE VENDA & GARANTIA          ")
    print("=" * 55)
    print(f"Cliente: {nome_cliente} (CPF: {cpf})")
    end_recibo = endereco_cliente if pode_ver_dados else "[ENDEREÇO PROTEGIDO / RESTRITO]"
    print(f"Endereço: {end_recibo}")
    print(f"Data da Operação: {data_venda_str}")
    print(f"Forma de Pagamento: {forma_pgto}")
    print("-" * 55)

    valor_total_pago = 0.0
    for it in carrinho:
        garantia_str = (data_hoje + timedelta(days=it['garantia_meses'] * 30)).strftime("%Y-%m-%d")
        venda = Venda(
            bateria_id=it['id_bat'],
            cliente_cpf=cpf,
            numero_serie=it['num_serie'],
            data_venda=data_venda_str,
            com_troca=it['com_troca'],
            valor_pago=it['valor_final'],
            forma_pagamento=forma_pgto,
            garantia_ate=garantia_str,
            cliente_nome=nome_cliente,
            cliente_endereco=endereco_cliente
        )
        VendaRepository.salvar(venda)
        BateriaRepository.decrementar_estoque(it['id_bat'])
        valor_total_pago += it['valor_final']
        print(f"• {it['marca']} {it['modelo']} | Série: {it['num_serie']} | R$ {it['valor_final']:.2f} | Gar. até: {garantia_str}")

    print("-" * 55)
    print(f"VALOR TOTAL RECEBIDO: R$ {valor_total_pago:.2f}")
    print("=" * 55)
    print("[SUCESSO] Venda finalizada e estoque atualizado com sucesso!")

def _processar_remocao_item_carrinho(carrinho):
    """Regra de negócio: Fiscal/Gerente pode remover item; Vendedor exige autorização."""
    if not carrinho:
        print("[INFO] Carrinho está vazio.")
        return

    # Verificar se o operador logado tem a permissão para remover item do carrinho
    if not SessaoSistema.tem_permissao("venda_remover_item"):
        print("\n" + "!" * 55)
        print("[PERMISSÃO REQUERIDA] Apenas Fiscal ou Gerente podem")
        print("cancelar ou retirar produtos do carrinho de vendas!")
        print("!" * 55)
        
        matricula_fiscal = input("Informe a Matrícula do Fiscal/Gerente para autorizar: ").strip()
        fiscal = FuncionarioRepository.buscar_por_matricula(matricula_fiscal)
        
        if not fiscal or not fiscal.tem_permissao("venda_remover_item"):
            print("\n[NEGADO] Matrícula inválida ou funcionário não possui cargo de Fiscal/Gerente!")
            print("Remoção de item cancelada.")
            return

        print(f"\n[AUTORIZADO] Remoção autorizada pelo Fiscal/Gerente: {fiscal.nome} ({fiscal.cargo.nome})")

    print("\nQual item deseja remover?")
    for idx, it in enumerate(carrinho, 1):
        print(f"[{idx}] {it['marca']} {it['modelo']} (Série: {it['num_serie']}) - R$ {it['valor_final']:.2f}")

    try:
        escolha = int(input("\nNúmero do item a retirar: "))
        if 1 <= escolha <= len(carrinho):
            item_removido = carrinho.pop(escolha - 1)
            print(f"\n[SUCESSO] Item '{item_removido['marca']} {item_removido['modelo']}' removido do carrinho!")
        else:
            print("[ERRO] Número de item inválido.")
    except ValueError:
        print("[ERRO] Entrada inválida.")

def consultar_vendas():
    """Consulta vendas realizadas com filtro de dados sensíveis por permissão de cargo."""
    if not (SessaoSistema.tem_permissao("venda_consultar") or SessaoSistema.tem_permissao("venda_realizar")):
        print("\n[ACESSO NEGADO] Seu cargo não possui permissão para consultar o histórico de vendas.")
        return
    print("\n--- CONSULTA DE VENDAS REALIZADAS ---")
    print("[1] Listar todas as vendas")
    print("[2] Buscar por CPF do Cliente")
    print("[3] Buscar por Número de Série da Bateria")
    opcao = input("Escolha o tipo de consulta: ").strip()
    
    parametro = None
    if opcao == '2':
        parametro = input("Digite o CPF do cliente: ").strip()
    elif opcao == '3':
        parametro = input("Digite o Nº de Série: ").strip()
    elif opcao != '1':
        print("[ERRO] Opção de busca inválida.")
        return

    vendas = VendaRepository.consultar_vendas(opcao, parametro)
    if not vendas:
        print("\n[INFO] Nenhuma venda encontrada para os critérios informados.")
        return

    pode_ver_dados = SessaoSistema.tem_permissao("cliente_ver_dados")

    print("\n" + "=" * 115)
    print(f"{'ID':<4} | {'Produto':<18} | {'CPF':<14} | {'Nome':<18} | {'Endereço':<25} | {'Nº Série':<12} | {'Valor':<8}")
    print("-" * 115)
    for v in vendas:
        # v: (id, marca, modelo, cpf, serie, data, valor, pgto, com_troca, cliente_nome, cliente_endereco)
        v_id, marca, modelo, cpf, serie, _, valor, _, _, nome_cli, end_cli = v
        
        nome_display = nome_cli if nome_cli else "Não inf."
        if pode_ver_dados:
            end_display = end_cli[:25] if end_cli else "Não inf."
        else:
            end_display = "[RESTRITO]"

        print(f"{v_id:<4} | {marca + ' ' + modelo:<18} | {cpf:<14} | {nome_display[:18]:<18} | {end_display:<25} | {serie:<12} | R$ {valor:<6.2f}")
    print("=" * 115)
    if not pode_ver_dados:
        print("[AVISO] Endereços completos de clientes estão ocultos. Requer cargo Fiscal/Gerente.")

def consultar_garantia():
    """Consulta o histórico de garantia da bateria vendida."""
    if not SessaoSistema.tem_permissao("garantia_consultar"):
        print("\n[ACESSO NEGADO] Seu cargo não possui permissão para consultar garantias.")
        return
    print("\n--- CONSULTA DE GARANTIA DO CLIENTE ---")
    busca = input("Digite o CPF do cliente ou o Nº de Série da bateria: ").strip()
    vendas = VendaRepository.buscar_garantia(busca)

    if not vendas:
        print("[INFO] Nenhuma venda localizada com o dado informado.")
        return

    hoje = datetime.now().date()
    pode_ver_dados = SessaoSistema.tem_permissao("cliente_ver_dados")

    print("\nHistórico de Garantia:")
    for v in vendas:
        v_id, marca, modelo, num_serie, cpf, d_venda, g_ate, _ = v
        dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
        status = "DENTRO DA GARANTIA" if hoje <= dt_garantia else "EXPIRADA"
        
        print("-" * 50)
        print(f"Registro: #{v_id} | Produto: {marca} {modelo}")
        print(f"Nº Série: {num_serie} | CPF: {cpf}")
        print(f"Data da Venda: {d_venda[:10]}")
        print(f"Garantia Até: {dt_garantia.strftime('%d/%m/%Y')} -> STATUS: [{status}]")