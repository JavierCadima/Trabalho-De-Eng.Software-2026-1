from models.sessao import SessaoSistema
from repositories.cliente_repository import ClienteRepository

def listar_clientes():
    """Consulta e lista clientes cadastrados com proteção de dados por permissão de cargo."""
    if not (SessaoSistema.tem_permissao("cliente_consultar") or SessaoSistema.tem_permissao("cliente_cadastrar") or SessaoSistema.tem_permissao("cliente_ver_dados")):
        print("\n[ACESSO NEGADO] Seu cargo não possui permissão para consultar o cadastro de clientes.")
        return
    print("\n--- CADASTRO DE CLIENTES ---")
    clientes = ClienteRepository.obter_todos()
    if not clientes:
        print("[INFO] Nenhum cliente cadastrado no momento.")
        return

    pode_ver_dados = SessaoSistema.tem_permissao("cliente_ver_dados")

    print("=" * 85)
    print(f"{'CPF':<15} | {'Nome':<25} | {'Endereço':<28} | {'Telefone':<12}")
    print("-" * 85)
    for c in clientes:
        end_str = c.endereco if pode_ver_dados else "[RESTRITO - FISCAL/GERENTE]"
        print(f"{c.cpf:<15} | {c.nome[:25]:<25} | {end_str[:28]:<28} | {c.telefone:<12}")
    print("=" * 85)
    if not pode_ver_dados:
        print("[AVISO] Endereços de clientes são visíveis apenas para Fiscais e Gerentes.")
