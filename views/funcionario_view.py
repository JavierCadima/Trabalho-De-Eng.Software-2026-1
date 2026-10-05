import sqlite3

from models.sessao import SessaoSistema
from models.funcionario import Funcionario
from models.cargo import Cargo
from repositories.funcionario_repository import FuncionarioRepository
from repositories.cargo_repository import CargoRepository

TODAS_PERMISSOES = [
    ("venda_realizar", "Realizar Vendas no PDV (Carrinho de Compras)"),
    ("venda_remover_item", "Retirar / Cancelar Itens do Carrinho de Vendas"),
    ("venda_consultar", "Consultar Histórico de Vendas Realizadas"),
    ("cliente_consultar", "Consultar Lista de Clientes Cadastrados"),
    ("cliente_cadastrar", "Cadastrar e Atualizar Clientes"),
    ("cliente_ver_dados", "Visualizar Dados Restritos de Clientes (Endereço Completo)"),
    ("estoque_consultar", "Consultar Estoque e Preços"),
    ("estoque_gerenciar", "Cadastrar Baterias, Repor Estoque e Alterar Preços"),
    ("garantia_consultar", "Consultar Garantias e Quantidade de Baterias Ruins"),
    ("garantia_troca", "Processar Trocas de Bateria por Defeito em Garantia"),
    ("relatorios_ver", "Visualizar Relatórios Gerenciais Completos"),
    ("area_gerente", "Acesso à Área do Gerente"),
    ("funcionarios_gerenciar", "Cadastrar e Visualizar Funcionários"),
    ("cargos_gerenciar", "Criar e Customizar Cargos (Exclusivo Administrador Principal)")
]

def identificar_operador():
    """Identifica o funcionário que está operando o sistema."""
    print("\n" + "=" * 50)
    print("        LOGIN / IDENTIFICAÇÃO DE OPERADOR        ")
    print("=" * 50)
    
    matricula = input("Digite a Matrícula do Funcionário (Ex: 1001): ").strip()
    if not matricula:
        print("[ERRO] Matrícula não pode ser vazia.")
        return False

    func = FuncionarioRepository.buscar_por_matricula(matricula)
    if not func:
        print(f"\n[ERRO] Funcionário com matrícula '{matricula}' não encontrado!")
        return False

    if not func.ativo:
        print(f"\n[BLOQUEADO] O funcionário '{func.nome}' está inativo no sistema.")
        return False

    if not func.is_administrador_principal():
        from getpass import getpass
        from repositories.funcionario_repository import FuncionarioRepository
        from utils.password_security import (
            avaliar_forca_senha,
            gerar_credencial,
            verificar_senha,
        )

        if not func.senha_hash or not func.senha_salt:
            print("\nPrimeiro acesso: cadastre sua senha pessoal.")
            while True:
                senha = getpass("Nova senha: ")
                confirmacao = getpass("Confirme a senha: ")
                if senha != confirmacao:
                    print("[ERRO] As senhas não conferem.")
                    continue
                forca, orientacao = avaliar_forca_senha(senha)
                print(f"Força da senha: {forca}. {orientacao}")
                if forca == "Fraca":
                    print("[ERRO] Cadastre uma senha pelo menos média.")
                    continue
                credencial = gerar_credencial(senha)
                try:
                    FuncionarioRepository.definir_credencial(
                        func.id, *credencial
                    )
                except (ValueError, sqlite3.Error) as erro:
                    print(f"[ERRO] Não foi possível cadastrar a senha: {erro}")
                    return False
                func.senha_hash, func.senha_salt = credencial
                break
        else:
            senha = getpass("Senha: ")
            if not verificar_senha(senha, func.senha_hash, func.senha_salt):
                print("[ERRO] Senha incorreta.")
                return False

    SessaoSistema.definir_operador(func)
    print(f"\n[SUCESSO] Bem-vindo(a), {func.nome}!")
    print(f"Cargo: {func.cargo.nome} | Matrícula: {func.matricula}")
    return True

def cadastrar_novo_funcionario():
    """Cadastra um novo funcionário associado a um cargo existente."""
    print("\n--- CADASTRO DE NOVO FUNCIONÁRIO ---")
    
    if not SessaoSistema.tem_permissao("funcionarios_gerenciar"):
        print("[ACESSO NEGADO] Você não tem permissão para cadastrar funcionários.")
        return

    matricula = input("Digite a Matrícula única do novo funcionário: ").strip()
    if not matricula:
        print("[ERRO] Matrícula não pode ser vazia.")
        return

    if any(f.matricula == matricula for f in FuncionarioRepository.obter_todos(apenas_ativos=False)):
        print(f"[ERRO] Já existe um funcionário com a matrícula '{matricula}'.")
        return

    nome = input("Nome completo do funcionário: ").strip()
    if not nome:
        print("[ERRO] Nome não pode ser vazio.")
        return

    operador = SessaoSistema.obter_operador()
    cargos = [
        cargo for cargo in CargoRepository.obter_todos()
        if not cargo.tem_permissao("cargos_gerenciar")
        and operador.cargo
        and cargo.nivel <= operador.cargo.nivel
    ]
    if not cargos:
        print("[ERRO] Nenhum cargo disponível no sistema.")
        return

    print("\nSelecione o Cargo:")
    for c in cargos:
        print(f"[{c.id}] {c.nome} (Nível {c.nivel})")

    try:
        cargo_id = int(input("\nOpção de Cargo (ID): "))
        cargo_escolhido = CargoRepository.buscar_por_id(cargo_id)
        if not cargo_escolhido:
            print("[ERRO] Cargo informado não existe.")
            return
        if (cargo_escolhido.tem_permissao("cargos_gerenciar")
                or not operador.cargo or cargo_escolhido.nivel > operador.cargo.nivel):
            print("[ERRO] Não é permitido atribuir cargo superior ao seu nível.")
            return
    except ValueError:
        print("[ERRO] ID do cargo inválido.")
        return

    novo_func = Funcionario(matricula=matricula, nome=nome, cargo=cargo_escolhido)
    FuncionarioRepository.salvar(novo_func)
    print(f"\n[SUCESSO] Funcionário '{nome}' (Matrícula: {matricula}) cadastrado com sucesso no cargo '{cargo_escolhido.nome}'!")

def listar_funcionarios():
    """Lista todos os funcionários cadastrados com matrícula, nome e cargo."""
    if not SessaoSistema.tem_permissao("funcionarios_gerenciar"):
        print("[ACESSO NEGADO] Você não tem permissão para consultar funcionários.")
        return

    print("\n--- LISTAGEM DE FUNCIONÁRIOS DO SISTEMA ---")
    funcionarios = FuncionarioRepository.obter_todos(apenas_ativos=False)
    
    if not funcionarios:
        print("[INFO] Nenhum funcionário cadastrado.")
        return

    print("=" * 65)
    print(f"{'ID':<4} | {'Matrícula':<12} | {'Nome':<25} | {'Cargo':<18}")
    print("-" * 65)
    for f in funcionarios:
        cargo_nome = f.cargo.nome if f.cargo else "Sem Cargo"
        status = "" if f.ativo else " [INATIVO]"
        print(f"{f.id:<4} | {f.matricula:<12} | {f.nome[:25]:<25} | {cargo_nome + status:<18}")
    print("=" * 65)

def redefinir_senha_funcionario():
    """Permite redefinir senha somente com autorização de cargo superior."""
    from getpass import getpass
    from utils.password_security import (
        avaliar_forca_senha,
        gerar_credencial,
        verificar_senha,
    )

    if not SessaoSistema.tem_permissao("funcionarios_gerenciar"):
        print("[ACESSO NEGADO] Você não tem permissão para redefinir senhas.")
        return
    operador = SessaoSistema.obter_operador()
    matricula = input("Matrícula do funcionário que precisa redefinir a senha: ").strip()
    funcionario = FuncionarioRepository.buscar_por_matricula(matricula)
    if not funcionario or not operador:
        print("[ERRO] Funcionário inexistente ou inativo.")
        return
    try:
        ativos = FuncionarioRepository.obter_todos(apenas_ativos=True)
    except sqlite3.Error as erro:
        print(f"[ERRO] Não foi possível validar a autorização: {erro}")
        return
    funcionario = next((item for item in ativos if item.id == funcionario.id), None)
    operador = next((item for item in ativos if item.id == operador.id), None)
    if not funcionario or not operador or not operador.tem_permissao("funcionarios_gerenciar"):
        print("[ACESSO NEGADO] O autorizador e o funcionário precisam estar ativos.")
        return
    if (funcionario.id == operador.id or not operador.cargo or not funcionario.cargo
            or operador.cargo.nivel <= funcionario.cargo.nivel):
        print("[ACESSO NEGADO] A redefinição exige outro cargo de nível superior.")
        return

    if not operador.is_administrador_principal():
        if not operador.senha_hash or not operador.senha_salt:
            print("[ACESSO NEGADO] Cadastre sua senha antes de autorizar redefinições.")
            return
        if not verificar_senha(
            getpass("Confirme sua senha para autorizar: "),
            operador.senha_hash,
            operador.senha_salt,
        ):
            print("[ACESSO NEGADO] Senha do autorizador incorreta.")
            return

    while True:
        senha = getpass("Nova senha para o funcionário: ")
        confirmacao = getpass("Confirme a nova senha: ")
        if senha != confirmacao:
            print("[ERRO] As senhas não conferem.")
            continue
        forca, orientacao = avaliar_forca_senha(senha)
        if forca == "Fraca":
            print(f"[ERRO] {orientacao}")
            continue
        try:
            FuncionarioRepository.definir_credencial(
                funcionario.id, *gerar_credencial(senha)
            )
        except (ValueError, sqlite3.Error) as erro:
            print(f"[ERRO] Não foi possível redefinir a senha: {erro}")
            return
        print(f"[SUCESSO] Senha redefinida. Força avaliada: {forca}.")
        return

def criar_novo_cargo():
    """
    Cria e customiza um novo cargo definindo suas permissões.
    RESTRITO EXCLUSIVAMENTE ao Administrador Principal.
    """
    print("\n--- CRIAÇÃO DE CARGO CUSTOMIZADO ---")

    # Verificação estrita exigida pelo usuário: apenas o Administrador Principal pode criar cargos
    if not SessaoSistema.is_administrador_principal():
        print("\n" + "!" * 65)
        print("[ACESSO RESTRITO] Apenas o Administrador Principal (Dono) tem")
        print("autorização para criar e customizar novos cargos e permissões!")
        print("!" * 65)
        return

    nome_cargo = input("Nome do Novo Cargo (Ex: Assistente de Estoque, Supervisor): ").strip()
    if not nome_cargo:
        print("[ERRO] O nome do cargo não pode ser vazio.")
        return

    if CargoRepository.buscar_por_nome(nome_cargo):
        print(f"[ERRO] Já existe um cargo com o nome '{nome_cargo}'.")
        return

    print(f"\nDefina as permissões para o cargo '{nome_cargo}':")
    permissoes_selecionadas = []

    for codigo, descricao in TODAS_PERMISSOES:
        # A permissão 'cargos_gerenciar' é reservada ao Dono
        if codigo == "cargos_gerenciar":
            continue

        resp = input(f" - Permitir {descricao}? (S/N) [Padrão: N]: ").strip().upper()
        if resp == 'S':
            permissoes_selecionadas.append(codigo)

    try:
        nivel = int(input("Nível hierárquico do cargo (1 a 999999; maior significa mais alto): "))
        novo_cargo = Cargo(nome=nome_cargo, permissoes=permissoes_selecionadas, nivel=nivel)
        CargoRepository.salvar(novo_cargo)
    except (ValueError, sqlite3.Error) as erro:
        print(f"[ERRO] Não foi possível criar o cargo: {erro}")
        return

    print("\n" + "=" * 55)
    print(f"[SUCESSO] Novo Cargo '{nome_cargo}' criado com sucesso!")
    print(f"Total de Permissões Concedidas: {len(permissoes_selecionadas)}")
    print("=" * 55)

def listar_cargos_e_permissoes():
    """Lista todos os cargos existentes e suas respectivas permissões ativas."""
    if not SessaoSistema.tem_permissao("cargos_gerenciar"):
        print("[ACESSO NEGADO] Você não tem permissão para consultar as permissões dos cargos.")
        return

    print("\n--- CARGOS E PERMISSÕES DO SISTEMA ---")
    cargos = CargoRepository.obter_todos()
    
    dict_descricoes = dict(TODAS_PERMISSOES)

    for c in cargos:
        print("=" * 60)
        print(f"CARGO [{c.id}]: {c.nome.upper()}")
        print("-" * 60)
        if not c.permissoes:
            print("  (Nenhuma permissão especial)")
        else:
            for p in c.permissoes:
                desc = dict_descricoes.get(p, p)
                print(f"  [✓] {desc} ({p})")
    print("=" * 60)
