from database.connection import conectar_bd
from views.bateria_view import cadastrar_bateria, repor_estoque, listar_estoque, atualizar_precificacao
from views.venda_view import realizar_venda, consultar_vendas, consultar_garantia
from views.troca_view import processar_troca_garantia, consultar_total_baterias_ruins
from views.relatorio_view import relatorio_gerencial

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