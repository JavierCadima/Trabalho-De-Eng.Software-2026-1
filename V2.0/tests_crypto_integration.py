import sqlite3
from models.bateria import Bateria
from models.venda import Venda
from models.troca import TrocaGarantia
from repositories.bateria_repository import BateriaRepository
from repositories.venda_repository import VendaRepository
from repositories.troca_repository import TrocaRepository
from utils.crypto import cifrar_texto, decifrar_texto, CHAVE_CESAR
from database.connection import conectar_bd

def test_crypto_functions():
    print("[1] Testando funções puras da Cifra de César...")
    original_text = "Moura M60GD - CPF: 123.456.789-00"
    cifrado = cifrar_texto(original_text, CHAVE_CESAR)
    decifrado = decifrar_texto(cifrado, CHAVE_CESAR)
    
    assert cifrado != original_text, "Texto cifrado deve ser diferente do original"
    assert decifrado == original_text, f"Esperado {original_text}, obtido {decifrado}"
    print(f"   Original : {original_text}")
    print(f"   Cifrado  : {cifrado}")
    print(f"   Decifrado: {decifrado}")
    print("   -> OK!")

def test_database_flow():
    print("\n[2] Testando persistência e busca com dados criptografados...")
    conectar_bd()
    
    # 1. Cadastrar Bateria
    bateria_teste = Bateria(
        marca="Heliar",
        modelo="HG60DD",
        amperagem=60,
        cca=520,
        voltagem=12,
        aplicacao="Sedan e SUV",
        garantia_meses=24,
        quantidade=10,
        preco_custo=300.0,
        preco_venda=480.0,
        preco_minimo=430.0,
        valor_carcaca=50.0
    )
    BateriaRepository.salvar(bateria_teste)
    
    # 2. Verificar o que foi gravado BRUTO no SQLite (como o DB Browser enxerga)
    conn = sqlite3.connect("loja_baterias.db")
    c = conn.cursor()
    c.execute("SELECT id, marca, modelo, aplicacao FROM baterias ORDER BY id DESC LIMIT 1")
    raw_bat = c.fetchone()
    conn.close()
    
    bat_id, raw_marca, raw_modelo, raw_aplicacao = raw_bat
    print(f"   [SQLite Bruto / DB Browser] Marca gravada: '{raw_marca}' | Modelo gravado: '{raw_modelo}'")
    assert raw_marca != "Heliar", "Marca deveria estar cifrada no banco bruto!"
    assert raw_marca == cifrar_texto("Heliar"), "Cifra da marca incorreta"
    assert raw_modelo == cifrar_texto("HG60DD"), "Cifra do modelo incorreta"
    
    # 3. Buscar via BateriaRepository (como o sistema enxerga)
    busca_res = BateriaRepository.buscar_baterias("heliar")
    assert len(busca_res) >= 1, "Deveria encontrar a bateria pela busca 'heliar'"
    encontrada = [b for b in busca_res if b[0] == bat_id][0]
    print(f"   [Aplicação / Sistema] Marca recuperada: '{encontrada[1]}' | Modelo: '{encontrada[2]}'")
    assert encontrada[1] == "Heliar", "Aplicação deve receber o dado decifrado"
    assert encontrada[2] == "HG60DD", "Aplicação deve receber o modelo decifrado"
    
    # 4. Cadastrar Venda
    venda_teste = Venda(
        bateria_id=bat_id,
        cliente_cpf="123.456.789-00",
        numero_serie="SERIE-9988-XYZ",
        data_venda="2026-09-16 22:00:00",
        com_troca=1,
        valor_pago=430.0,
        forma_pagamento="PIX",
        garantia_ate="2028-09-16"
    )
    VendaRepository.salvar(venda_teste)
    
    # 5. Verificar Venda no SQLite Bruto
    conn = sqlite3.connect("loja_baterias.db")
    c = conn.cursor()
    c.execute("SELECT id, cliente_cpf, numero_serie, forma_pagamento FROM vendas ORDER BY id DESC LIMIT 1")
    v_id, raw_cpf, raw_serie, raw_pgto = c.fetchone()
    conn.close()
    
    print(f"   [SQLite Bruto / DB Browser] CPF gravado: '{raw_cpf}' | Série: '{raw_serie}' | Pgto: '{raw_pgto}'")
    assert raw_cpf != "123.456.789-00", "CPF deveria estar cifrado no banco bruto!"
    assert raw_cpf == cifrar_texto("123.456.789-00"), "Cifra do CPF incorreta"
    
    # 6. Consultar Venda via VendaRepository
    vendas_cpf = VendaRepository.consultar_vendas('2', "123.456.789-00")
    assert len(vendas_cpf) >= 1, "Deveria encontrar venda buscando pelo CPF claro"
    venda_recup = [v for v in vendas_cpf if v[0] == v_id][0]
    print(f"   [Aplicação / Sistema] CPF recuperado: '{venda_recup[3]}' | Série: '{venda_recup[4]}'")
    assert venda_recup[3] == "123.456.789-00"
    assert venda_recup[4] == "SERIE-9988-XYZ"
    
    # 7. Buscar Garantia
    garantia_res = VendaRepository.buscar_garantia("SERIE-9988-XYZ")
    assert len(garantia_res) >= 1, "Deveria encontrar garantia pelo número de série"
    assert garantia_res[0][3] == "SERIE-9988-XYZ"
    
    # 8. Cadastrar Troca
    troca_teste = TrocaGarantia(
        venda_id=v_id,
        bateria_id=bat_id,
        numero_serie_defeito="SERIE-9988-XYZ",
        defeito_relatado="Placa em curto",
        data_troca="2026-09-17 10:00:00"
    )
    TrocaRepository.salvar(troca_teste)
    
    # 9. Relatório Gerencial
    _, defeitos = TrocaRepository.ob_dados = TrocaRepository.obter_dados_relatorio()
    assert len(defeitos) >= 1
    d_encontrado = [d for d in defeitos if d[3] == "SERIE-9988-XYZ"][0]
    print(f"   [Aplicação / Sistema] Troca recuperada: Série Defeito='{d_encontrado[3]}' | Defeito='{d_encontrado[4]}'")
    assert d_encontrado[3] == "SERIE-9988-XYZ"
    assert d_encontrado[4] == "Placa em curto"
    
    # Limpeza dos registros de teste
    conn = sqlite3.connect("loja_baterias.db")
    c = conn.cursor()
    c.execute("DELETE FROM trocas_garantia WHERE venda_id = ?", (v_id,))
    c.execute("DELETE FROM vendas WHERE id = ?", (v_id,))
    c.execute("DELETE FROM baterias WHERE id = ?", (bat_id,))
    conn.commit()
    conn.close()
    print("\n   -> OK! Todos os fluxos testados com sucesso e dados de teste limpos.")

if __name__ == "__main__":
    test_crypto_functions()
    test_database_flow()
    print("\nTODOS OS TESTES PASSARAM COM 100% DE SUCESSO!")

