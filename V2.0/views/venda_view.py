from datetime import datetime, timedelta
from models.venda import Venda
from repositories.bateria_repository import BateriaRepository
from repositories.venda_repository import VendaRepository
from views.bateria_view import selecionar_bateria_da_busca

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
    
    valor_base = p_venda - (v_carcaca if com_troca else 0)
    if com_troca:
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
    garantia_str = (data_hoje + timedelta(days=garantia_meses * 30)).strftime("%Y-%m-%d")

    venda = Venda(id_bat, cpf, num_serie, data_venda_str, com_troca, valor_final, forma_pgto, garantia_str)
    VendaRepository.salvar(venda)
    BateriaRepository.decrementar_estoque(id_bat)
    
    print("\n" + "="*40)
    print("      COMPROVANTE DE VENDA & GARANTIA      ")
    print("="*40)
    print(f"Produto: {marca} {modelo}")
    print(f"Nº de Série: {num_serie}")
    print(f"Cliente (CPF): {cpf}")
    print(f"Valor Pago: R$ {valor_final:.2f} ({forma_pgto})")
    print(f"Garantia Válida até: {(data_hoje + timedelta(days=garantia_meses * 30)).strftime('%d/%m/%Y')}")
    print("="*40)

def consultar_vendas():
    print("\n--- CONSULTA DE VENDAS ---")
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

    print("\n" + "="*95)
    print(f"{'ID':<4} | {'Produto':<18} | {'CPF Cliente':<14} | {'Nº Série':<14} | {'Data':<10} | {'Valor':<9} | {'Pgto':<10}")
    print("-" * 95)
    for v in vendas:
        print(f"{v[0]:<4} | {v[1] + ' ' + v[2]:<18} | {v[3]:<14} | {v[4]:<14} | {v[5][:10]:<10} | R$ {v[6]:<6.2f} | {v[7]:<10}")
    print("="*95)

def consultar_garantia():
    print("\n--- CONSULTA DE GARANTIA DO CLIENTE ---")
    busca = input("Digite o CPF do cliente ou o Nº de Série da bateria: ").strip()
    vendas = VendaRepository.buscar_garantia(busca)

    if not vendas:
        print("[INFO] Nenhuma venda localizada com o dado informado.")
        return

    hoje = datetime.now().date()
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