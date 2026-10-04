from models.sessao import SessaoSistema
from views.relatorio_view import relatorio_gerencial
from views.funcionario_view import (
    cadastrar_novo_funcionario, 
    listar_funcionarios, 
    criar_novo_cargo, 
    listar_cargos_e_permissoes,
    redefinir_senha_funcionario,
)

def menu_area_gerente():
    """Abre o painel de gestão com opções dinâmicas por permissão."""
    if not any(SessaoSistema.tem_permissao(permissao) for permissao in (
            "area_gerente", "relatorios_ver", "funcionarios_gerenciar",
            "cargos_gerenciar")):
        print("\n" + "!" * 55)
        print("[ACESSO NEGADO] Seu cargo atual não possui permissão")
        print("para acessar a Área de Gestão!")
        print("!" * 55)
        return

    while True:
        op = SessaoSistema.obter_operador()
        cargo_nome = op.cargo.nome if op and op.cargo else "Sem Cargo"
        
        print("\n" + "=" * 55)
        print("            PAINEL DA ÁREA DO GERENTE            ")
        print(f" Operador: {op.nome} | Cargo: {cargo_nome}")
        print("=" * 55)

        opcoes_gerente = []

        if SessaoSistema.tem_permissao("relatorios_ver"):
            opcoes_gerente.append(("Relatório Gerencial Completo (Vendas & Faturamento)", relatorio_gerencial))

        if SessaoSistema.tem_permissao("funcionarios_gerenciar"):
            opcoes_gerente.append(("Cadastrar Novo Funcionário", cadastrar_novo_funcionario))
            opcoes_gerente.append(("Listar Funcionários e Cargos Cadastrados", listar_funcionarios))
            opcoes_gerente.append(("Redefinir Senha de Funcionário", redefinir_senha_funcionario))

        # A opção de criar/customizar cargos é exibida APENAS para o Administrador Principal
        if SessaoSistema.tem_permissao("cargos_gerenciar"):
            opcoes_gerente.append(("Criar Novo Cargo Customizável (Exclusivo Administrador)", criar_novo_cargo))

        if SessaoSistema.tem_permissao("cargos_gerenciar"):
            opcoes_gerente.append(("Consultar Permissões de Todos os Cargos", listar_cargos_e_permissoes))

        for idx, (label, _) in enumerate(opcoes_gerente, 1):
            print(f"[{idx}] {label}")
        print("[0] Voltar ao Menu Principal")

        escolha = input("\nEscolha uma opção do Gerente: ").strip()
        if escolha == '0':
            break

        try:
            num = int(escolha)
            if 1 <= num <= len(opcoes_gerente):
                _, func = opcoes_gerente[num - 1]
                func()
            else:
                print("\n[ERRO] Opção inválida! Escolha um número listado acima.")
        except ValueError:
            print("\n[ERRO] Digite um número válido!")
