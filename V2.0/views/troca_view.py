from datetime import datetime
from models.troca import TrocaGarantia
from repositories.bateria_repository import BateriaRepository
from repositories.venda_repository import VendaRepository
from repositories.troca_repository import TrocaRepository

def processar_troca_garantia():
    print("\n--- TROCA DE BATERIA DEFEITUOSA (GARANTIA) ---")
    busca = input("Digite o CPF do Cliente ou Nº de Série da bateria com defeito: ").strip()
    vendas = VendaRepository.buscar_garantia(busca)
    
    if not vendas:
        print("[ERRO] Nenhuma venda localizada para os dados informados.")
        return

    print("\nSelecione qual item está apresentando defeito:")
    for idx, v in enumerate(vendas, 1):
        v_id, marca, modelo, num_serie, cpf, _, g_ate, _ = v
        dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
        status_g = "DENTRO DA GARANTIA" if datetime.now().date() <= dt_garantia else "EXPIRADA"
        print(f"[{idx}] Venda #{v_id} | {marca} {modelo} | Nº Série: {num_serie} | Vencimento Garantia: {dt_garantia.strftime('%d/%m/%Y')} [{status_g}]")

    try:
        op = int(input("\nOpção correspondente: ")) - 1
        venda_sel = vendas[op]
    except (ValueError, IndexError):
        print("[ERRO] Seleção inválida.")
        return

    v_id, marca, modelo, num_serie_antigo, cpf, _, g_ate, bat_id = venda_sel[0], venda_sel[1], venda_sel[2], venda_sel[3], venda_sel[4], venda_sel[5], venda_sel[6], venda_sel[7]
    dt_garantia = datetime.strptime(g_ate, "%Y-%m-%d").date()
    
    if datetime.now().date() > dt_garantia:
        print("\n[ALERTA] A garantia desta bateria está EXPIRADA!")
        confirmar = input("Deseja realizar a troca em caráter de exceção/cortesia? (S/N): ").strip().upper()
        if confirmar != 'S':
            return

    qtd_estoque = BateriaRepository.obter_quantidade_estoque(bat_id)
    if qtd_estoque <= 0:
        print(f"\n[ERRO] Não há baterias novas de reposição ({marca} {modelo}) em estoque!")
        return

    defeito = input("Informe o defeito constatado (Ex: Placa em curto, Vazamento, Não segura carga): ").strip()
    num_serie_novo = input("Digite o Nº de Série da NOVA bateria que será entregue: ").strip()
    data_hoje_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    troca = TrocaGarantia(v_id, bat_id, num_serie_antigo, defeito, data_hoje_str)
    TrocaRepository.salvar(troca)
    
    VendaRepository.atualizar_numero_serie(v_id, num_serie_novo)
    BateriaRepository.decrementar_estoque(bat_id)

    print("\n" + "="*50)
    print("   TROCA EM GARANTIA REALIZADA COM SUCESSO!   ")
    print("="*50)
    print(f"Bateria Devolvida (Ruim): {marca} {modelo} | Série: {num_serie_antigo}")
    print(f"Defeito Anotado: {defeito}")
    print(f"Nova Bateria Entregue: Série {num_serie_novo}")
    print("="*50)

def consultar_total_baterias_ruins():
    carcacas_troca, garantias_defeito = TrocaRepository.obter_totais_ruins()
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