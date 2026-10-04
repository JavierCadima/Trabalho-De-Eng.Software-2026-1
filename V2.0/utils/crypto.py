import random
import time
import math
import re
"""
Módulo de Criptografia - Cifra de César
Implementa algoritmos de cifra por substituição monoalfabética (deslocamento)
para ofuscação de dados confidenciais armazenados no banco de dados SQLite.
"""

class CriptografiaCustomizada:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # 1. Funções Matemáticas para Números (CPF / Matrícula)
    # ------------------------------------------------------------------
    @staticmethod
    def _f1(x): return int(x**3 - 2 * x**2 + 5 * x + 10)
    
    @staticmethod
    def _f2(x): return int(abs(math.sin(x) * 100) + 15)
    
    @staticmethod
    def _f3(x): return int(2**x + 3 * x)
    
    @staticmethod
    def _f4(x): return int(math.factorial(x % 8) + 7 * x)

    def processar_numeros(self, texto_numerico):
        """Aplica as 4 funções matemáticas aos dígitos."""
        resultados = []
        for digito in str(texto_numerico):
            if digito.isdigit():
                x = int(digito)
                v1, v2, v3, v4 = self._f1(x), self._f2(x), self._f3(x), self._f4(x)
                resultados.append(f"{x}:{v1}-{v2}-{v3}-{v4}")
        return "|".join(resultados) if resultados else "SEM_NUMEROS"

    # ------------------------------------------------------------------
    # 2. Manipulação de Letras Repetidas (2 a 5)
    # ------------------------------------------------------------------
    def _substituir_repetidas(self, texto):
        padrao = re.compile(r'((.)\2{1,4})')
        trocas_realizadas = []

        def substituir(match):
            grupo = match.group(1)
            tamanho = len(grupo)
            substituto = "".join([chr(random.randint(65, 90)) for _ in range(tamanho)])
            trocas_realizadas.append(f"{grupo}->{substituto}")
            return substituto

        texto_alterado = padrao.sub(substituir, texto)
        string_trocas = ",".join(trocas_realizadas) if trocas_realizadas else "SEM_TROCAS"
        return texto_alterado, string_trocas

    def _restaurar_repetidas(self, texto, mapa_trocas):
        if mapa_trocas == "SEM_TROCAS" or not mapa_trocas:
            return texto

        texto_restaurado = texto
        for troca in mapa_trocas.split(","):
            if "->" in troca:
                original, substituto = troca.split("->")
                texto_restaurado = texto_restaurado.replace(substituto, original, 1)

        return texto_restaurado

    # ------------------------------------------------------------------
    # 3. Cifra de César
    # ------------------------------------------------------------------
    def _cifra_cesar(self, texto, deslocamento, modo='criptografar'):
        if modo == 'descriptografar':
            deslocamento = -deslocamento

        resultado = []
        for char in texto:
            if char.isascii() and char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                resultado.append(chr((ord(char) - base + deslocamento) % 26 + base))
            else:
                resultado.append(char)
        return "".join(resultado)

    def _extrair_digitos_chave(self, mapa_matematico):
        if not mapa_matematico or mapa_matematico == "SEM_NUMEROS":
            return ""
        return "".join([item.split(":")[0] for item in mapa_matematico.split("|") if ":" in item])

    # ------------------------------------------------------------------
    # 4. Método CRIPTOGRAFAR (1 único objeto por chamada)
    # ------------------------------------------------------------------
    def criptografar(self, objeto):
        if objeto is None:
            return None
        dado_str = str(objeto).strip()
        if not dado_str:
            return ""
        
        tempo_os = int(time.time_ns())
        random.seed(tempo_os)
        deslocamento = random.randint(1, 25)

        if dado_str.isdigit():
            # Estrutura para CPF / Número puro
            texto_cifrado = "DADONUMERICO"
            mapa_trocas = "SEM_TROCAS"
            mapa_matematico = self.processar_numeros(dado_str)
        else:
            # Estrutura para Frase / Texto
            texto_sem_repeticao, mapa_trocas = self._substituir_repetidas(dado_str)
            texto_cifrado = self._cifra_cesar(texto_sem_repeticao, deslocamento, modo='criptografar')
            
            numeros_encontrados = "".join(re.findall(r'\d+', dado_str))
            mapa_matematico = self.processar_numeros(numeros_encontrados) if numeros_encontrados else "SEM_NUMEROS"

        # Formato do delimitador: [CHAVE]_[TEXTOCIFRADO]
        chave = f"{tempo_os}#{deslocamento}#{mapa_trocas}#{mapa_matematico}"
        return f"{chave}_{texto_cifrado}"

    # ------------------------------------------------------------------
    # 5. Método DESCRIPTOGRAFAR
    # ------------------------------------------------------------------
    def descriptografar(self, hash_criptografado):
        if hash_criptografado is None:
            return None
        s_hash = str(hash_criptografado)
        if not s_hash:
            return ""
            
        try:
            if "#" in s_hash:
                partes = s_hash.split("#", 3)
                deslocamento = int(partes[1])
                mapa_trocas = partes[2]
                resto = partes[3]
                if resto.startswith("SEM_NUMEROS_"):
                    mapa_matematico = "SEM_NUMEROS"
                    texto_cifrado = resto[len("SEM_NUMEROS_"):]
                elif "_" in resto:
                    mapa_matematico, texto_cifrado = resto.split("_", 1)
                else:
                    mapa_matematico = resto
                    texto_cifrado = ""
            else:
                partes_hash = s_hash.rsplit("_", 1)
                chave = partes_hash[0]
                texto_cifrado = partes_hash[1] if len(partes_hash) > 1 else ""
                partes = chave.split("#")
                deslocamento = int(partes[1])
                mapa_trocas = partes[2]
                mapa_matematico = partes[3]

            # Caso 1: Dado é um CPF/Número puro
            if texto_cifrado == "DADONUMERICO":
                return self._extrair_digitos_chave(mapa_matematico)

            # Caso 2: Dado é um Texto
            texto_cesar = self._cifra_cesar(texto_cifrado, deslocamento, modo='descriptografar')
            texto_original = self._restaurar_repetidas(texto_cesar, mapa_trocas)
            return texto_original

        except Exception as e:
            return f"Erro ao descriptografar: {str(e)}"


# Singleton para uso nos Repositórios
_cripto_instance = CriptografiaCustomizada()

def cifrar_texto(texto):
    """Encapsulador para compatibilidade direta com os repositórios."""
    return _cripto_instance.criptografar(texto)

def decifrar_texto(texto_cifrado):
    """Encapsulador para compatibilidade direta com os repositórios."""
    return _cripto_instance.descriptografar(texto_cifrado)
