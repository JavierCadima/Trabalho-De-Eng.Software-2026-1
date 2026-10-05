from models.bateria import Bateria
from models.sessao import SessaoSistema
from repositories.bateria_repository import BateriaRepository

def selecionar_bateria_da_busca(termo):
    baterias = BateriaRepository.buscar_baterias(termo)
    if not baterias:
        print("[ERRO] Nenhuma bateria encontrada com o termo informado.")
        return None
    if len(baterias) == 1:
        return baterias[0]
        
    print("\nForam encontradas múltiplas baterias. Escolha uma abaixo:")
    print(f"{'ID':<4} | {'Marca/Modelo':<20} | {'Espec.':<10} | {'Estoque':<8} | {'Preço Tabela':<12}")
    print("-" * 60)
    for b in baterias:
        print(f"{b[0]:<4} | {b[1] + ' ' + b[2]:<20} | {b[3]}Ah/{b[4]}A | {b[5]:<8} | R$ {b[6]:.2f}")
        
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

def cadastrar_bateria():
    if not SessaoSistema.tem_permissao("estoque_gerenciar"):
        print("\n[ACESSO NEGADO] Seu cargo não tem permissão para cadastrar baterias.")
        return
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

        nova_bateria = Bateria(marca, modelo, amperagem, cca, voltagem, aplicacao, 
                               garantia_meses, quantidade, preco_custo, preco_venda, 
                               preco_minimo, valor_carcaca)
        BateriaRepository.salvar(nova_bateria)
        print("\n[SUCESSO] Novo modelo cadastrado com sucesso!")
    except ValueError:
        print("\n[ERRO] Entrada inválida! Verifique os valores numéricos digitados.")

def repor_estoque():
    if not SessaoSistema.tem_permissao("estoque_gerenciar"):
        print("\n[ACESSO NEGADO] Seu cargo não tem permissão para repor estoque.")
        return
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

        BateriaRepository.adicionar_estoque(id_bat, qtd_add)
        print(f"\n[SUCESSO] Estoque atualizado! Novo total: {qtd_atual + qtd_add} unidades.")
    except ValueError:
        print("[ERRO] Quantidade inválida.")

def listar_estoque():
    if not SessaoSistema.tem_permissao("estoque_consultar"):
        print("\n[ACESSO NEGADO] Seu cargo não tem permissão para consultar estoque.")
        return
    print("\n--- CONSULTA DE ESTOQUE E PREÇOS ---")
    baterias = BateriaRepository.obter_todas()
    if not baterias:
        print("Nenhuma bateria encontrada no cadastro.")
        return

    print(f"{'ID':<3} | {'Marca/Modelo':<18} | {'Espec.':<10} | {'Aplicação':<25} | {'Qtd':<8} | {'Tabela':<9} | {'Mínimo':<9} | {'Carcaça':<8}")
    print("-" * 103)
    for b in baterias:
        id_bat, marca, modelo, ah, cca, aplicacao, qtd, p_venda, p_min, v_carcaca = b
        alerta = " (BAIXO!)" if qtd <= 2 else ""
        print(f"{id_bat:<3} | {marca + ' ' + modelo:<18} | {ah}Ah/{cca}A:<10 | {aplicacao[:25]:<25} | {str(qtd) + alerta:<8} | R$ {p_venda:<6.2f} | R$ {p_min:<6.2f} | R$ {v_carcaca:<6.2f}")

def atualizar_precificacao():
    if not SessaoSistema.tem_permissao("estoque_gerenciar"):
        print("\n[ACESSO NEGADO] Seu cargo não tem permissão para alterar preços.")
        return
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

        BateriaRepository.atualizar_precos(bateria_id, novo_venda, novo_minimo, novo_carcaca)
        print("\n[SUCESSO] Preços atualizados com sucesso!")
    except ValueError:
        print("[ERRO] Valores digitados são inválidos.")