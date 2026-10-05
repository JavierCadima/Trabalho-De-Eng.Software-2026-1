from repositories.troca_repository import TrocaRepository
from models.sessao import SessaoSistema

def relatorio_gerencial():
    if not SessaoSistema.tem_permissao("relatorios_ver"):
        print("\n[ACESSO NEGADO] Seu cargo não tem permissão para visualizar relatórios gerenciais.")
        return
    print("\n--- RELATÓRIOS GERENCIAIS ---")
    res_vendas, defeitos = TrocaRepository.obter_dados_relatorio()
    
    total_vendas = res_vendas[0] or 0
    faturamento = res_vendas[1] or 0.0
    total_carcacas = res_vendas[2] or 0

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
            d_id, marca, modelo, serie_def, def_rel, _, _ = d
            print(f"{d_id:<3} | {marca + ' ' + modelo:<18} | {serie_def:<18} | {def_rel[:25]:<25}")