from database.connection import get_connection

class ConfiguracaoRepository:
    def get_parametro(self, chave: str, default=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return default

        valor = row[0]
        if isinstance(default, float):
            try:
                return float(valor)
            except (TypeError, ValueError):
                return default
        if isinstance(default, int):
            try:
                return int(valor)
            except (TypeError, ValueError):
                return default
        return valor

    def set_parametro(self, chave: str, valor):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)",
            (chave, str(valor))
        )
        conn.commit()
        conn.close()

    def get_desconto_cnpj(self) -> float:
        return self.get_parametro("desconto_cnpj", 10.0)

    def set_desconto_cnpj(self, percentual: float):
        self.set_parametro("desconto_cnpj", percentual)

    def get_desconto_cpf(self) -> float:
        return self.get_parametro("desconto_cpf", 0.0)

    def set_desconto_cpf(self, percentual: float):
        self.set_parametro("desconto_cpf", percentual)

    def get_desconto_pix(self) -> float:
        return self.get_parametro("desconto_pix", 5.0)

    def set_desconto_pix(self, percentual: float):
        self.set_parametro("desconto_pix", percentual)

    def get_desconto_dinheiro(self) -> float:
        return self.get_parametro("desconto_dinheiro", 5.0)

    def set_desconto_dinheiro(self, percentual: float):
        self.set_parametro("desconto_dinheiro", percentual)

    def get_desconto_qtd_minima_percentual(self) -> float:
        return self.get_parametro("desconto_qtd_minima_percentual", 3.0)

    def set_desconto_qtd_minima_percentual(self, percentual: float):
        self.set_parametro("desconto_qtd_minima_percentual", percentual)

    def get_desconto_qtd_minima_qtd(self) -> int:
        return self.get_parametro("desconto_qtd_minima_qtd", 3)

    def set_desconto_qtd_minima_qtd(self, quantidade: int):
        self.set_parametro("desconto_qtd_minima_qtd", quantidade)
