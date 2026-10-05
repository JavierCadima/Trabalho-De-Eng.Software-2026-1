-- TABELA DE BATERIAS
CREATE TABLE IF NOT EXISTS baterias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    amperagem INTEGER NOT NULL,
    cca INTEGER NOT NULL,
    voltagem INTEGER NOT NULL,
    aplicacao TEXT NOT NULL,
    garantia_meses INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_custo REAL NOT NULL,
    preco_venda REAL NOT NULL,
    preco_minimo REAL NOT NULL,
    valor_carcaca REAL NOT NULL
);

-- TABELA DE VENDAS
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bateria_id INTEGER NOT NULL,
    cliente_cpf TEXT NOT NULL,
    numero_serie TEXT NOT NULL,
    data_venda TEXT NOT NULL,
    com_troca INTEGER NOT NULL,
    valor_pago REAL NOT NULL,
    forma_pagamento TEXT NOT NULL,
    garantia_ate TEXT NOT NULL,
    FOREIGN KEY (bateria_id) REFERENCES baterias (id)
);

-- ESTOQUE INICIAL DE BATERIAS
INSERT INTO baterias (marca, modelo, amperagem, cca, voltagem, aplicacao, garantia_meses, quantidade, preco_custo, preco_venda, preco_minimo, valor_carcaca) VALUES
('Moura', 'M60AD', 60, 460, 12, 'Passeio (Gol, Onix, HB20)', 18, 15, 320.0, 480.0, 440.0, 50.0),
('Moura', 'M50ED', 50, 380, 12, 'Compactos (Uno, Palio, Ka)', 18, 10, 280.0, 410.0, 380.0, 40.0),
('Moura', 'M70KD', 70, 520, 12, 'SUVs / Sedans (Corolla, Civic)', 18, 8, 390.0, 580.0, 530.0, 60.0),
('Heliar', 'HG60DD', 60, 480, 12, 'Passeio Premium', 24, 12, 340.0, 510.0, 470.0, 50.0),
('Heliar EFB', 'EFB60', 60, 530, 12, 'Start-Stop (Renegade, Compass)', 24, 5, 520.0, 780.0, 720.0, 70.0),
('Tudor', 'T50ED', 50, 380, 12, 'Econômica Passeio', 15, 8, 230.0, 350.0, 320.0, 40.0),
('Bosch', 'S6 AGM', 60, 600, 12, 'Importados / Start-Stop', 24, 3, 650.0, 980.0, 900.0, 80.0),
('Moura Moto', 'MA5-D', 5, 70, 12, 'Motos (CG 160, Bros)', 12, 20, 110.0, 180.0, 160.0, 15.0),
('Moura Pesada', 'M150BD', 150, 900, 12, 'Caminhões / Ônibus', 15, 4, 720.0, 1080.0, 990.0, 120.0),
('Freedom', 'DF2000', 115, 600, 12, 'Nobreak / Solar', 24, 6, 600.0, 890.0, 820.0, 0.0);

-- HISTÓRICO INICIAL DE VENDAS
INSERT INTO vendas (bateria_id, cliente_cpf, numero_serie, data_venda, com_troca, valor_pago, forma_pagamento, garantia_ate) VALUES
(1, '12345678900', 'M60-SN-8821', '2025-11-10 14:20:00', 1, 430.0, 'PIX', '2027-05-10'),
(4, '98765432100', 'HEL-SN-1102', '2026-01-05 09:15:00', 1, 460.0, 'Cartão de Crédito', '2028-01-05');