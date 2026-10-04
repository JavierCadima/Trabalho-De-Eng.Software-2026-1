from database.connection import conectar_bd
from models.sessao import SessaoSistema
from views.bateria_view import cadastrar_bateria, repor_estoque, listar_estoque, atualizar_precificacao
from views.venda_view import realizar_venda, consultar_vendas, consultar_garantia
from views.troca_view import processar_troca_garantia, consultar_total_baterias_ruins
from views.funcionario_view import identificar_operador
from views.gerente_view import menu_area_gerente
from views.cliente_view import listar_clientes

def menu():
    conectar_bd()

    # Identificação inicial obrigatória do operador
    while not SessaoSistema.obter_operador():
        print("\nPara iniciar o sistema, informe a matrícula do operador.")
        print("[Dica: Use 1001 para Administrador Principal, 2001 para Fiscal ou 3001 para Vendedor]")
        sucesso = identificar_operador()
        if not sucesso:
            resp = input("Deseja tentar novamente? (S/N) [Padrão: S]: ").strip().upper()
            if resp == 'N':
                print("\nEncerrando o sistema...")
                return

    while True:
        operador = SessaoSistema.obter_operador()
        cargo_nome = operador.cargo.nome if operador and operador.cargo else "Sem Cargo"
        
        print("\n" + "=" * 55)
        print("        SISTEMA DE GESTÃO - LOJA DE BATERIAS         ")
        print(f" OPERADOR: {operador.nome} | CARGO: {cargo_nome} (Matrícula: {operador.matricula})")
        print("=" * 55)

        opcoes_disponiveis = []

        # 1. Estoque e Produtos
        if SessaoSistema.tem_permissao("estoque_consultar"):
            opcoes_disponiveis.append(("Consultar Estoque e Preços", listar_estoque))

        if SessaoSistema.tem_permissao("estoque_gerenciar"):
            opcoes_disponiveis.append(("Cadastrar Novo Modelo de Bateria", cadastrar_bateria))
            opcoes_disponiveis.append(("Adicionar Estoque (Reposição de Unidades)", repor_estoque))
            opcoes_disponiveis.append(("Ajustar Precificação / Preço Mínimo", atualizar_precificacao))

        # 2. Vendas e Clientes (SÓ APARECEM SE O CARGO TIVER PERMISSÃO!)
        if SessaoSistema.tem_permissao("venda_realizar"):
            opcoes_disponiveis.append(("Realizar Venda (PDV - Carrinho de Compras)", realizar_venda))

        if SessaoSistema.tem_permissao("venda_consultar") or SessaoSistema.tem_permissao("venda_realizar"):
            opcoes_disponiveis.append(("Consultar Vendas Realizadas", consultar_vendas))

        if SessaoSistema.tem_permissao("cliente_consultar") or SessaoSistema.tem_permissao("cliente_ver_dados"):
            opcoes_disponiveis.append(("Consultar Clientes Cadastrados", listar_clientes))

        # 3. Garantias e Trocas
        if SessaoSistema.tem_permissao("garantia_consultar"):
            opcoes_disponiveis.append(("Consultar Garantia do Cliente", consultar_garantia))

        if SessaoSistema.tem_permissao("garantia_troca"):
            opcoes_disponiveis.append(("Registrar Troca de Bateria Defeituosa (Garantia)", processar_troca_garantia))

        if SessaoSistema.tem_permissao("garantia_consultar") or SessaoSistema.tem_permissao("estoque_consultar"):
            opcoes_disponiveis.append(("Consultar Quantidade de Baterias Ruins", consultar_total_baterias_ruins))

        # 4. Área do Gerente (SÓ APARECE SE TIVER ACESSO!)
        if (SessaoSistema.tem_permissao("area_gerente")
                or SessaoSistema.tem_permissao("relatorios_ver")
                or SessaoSistema.tem_permissao("funcionarios_gerenciar")
                or SessaoSistema.tem_permissao("cargos_gerenciar")):
            opcoes_disponiveis.append(("Área de Gestão (Relatórios & Equipe)", menu_area_gerente))

        # Opção de troca de usuário
        opcoes_disponiveis.append(("Trocar de Operador / Fazer Novo Login", identificar_operador))

        # Renderização dinâmica do menu
        for idx, (label, _) in enumerate(opcoes_disponiveis, 1):
            print(f"[{idx}] {label}")
        print("[0] Sair do Sistema")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == '0':
            print("\nEncerrando o sistema... Até logo!")
            break

        try:
            num = int(escolha)
            if 1 <= num <= len(opcoes_disponiveis):
                _, func = opcoes_disponiveis[num - 1]
                func()
            else:
                print("\n[ERRO] Opção inválida! Escolha um número exibido no menu.")
        except ValueError:
            print("\n[ERRO] Digite um número válido!")

if __name__ == "__main__":
    import sys

    if "--terminal" in sys.argv:
        menu()
    else:
        from desktop_app import iniciar_interface

        iniciar_interface()