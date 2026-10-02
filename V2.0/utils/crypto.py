"""
Módulo de Criptografia - Cifra de César
Implementa algoritmos de cifra por substituição monoalfabética (deslocamento)
para ofuscação de dados confidenciais armazenados no banco de dados SQLite.

teste 1wsbvwyh
"""

CHAVE_CESAR = 3  # Deslocamento clássico da Cifra de César (A -> D, 0 -> 3)

def cifrar_texto(texto: str, shift: int = CHAVE_CESAR) -> str:
    """
    Cifra uma string aplicando a Cifra de César com deslocamento 'shift'.
    Desloca caracteres alfabéticos (a-z, A-Z) e dígitos numéricos (0-9).
    Pontuações, espaços e caracteres com acentos são preservados.
    """
    if texto is None:
        return None
    if not isinstance(texto, str):
        texto = str(texto)
        
    resultado = []
    for char in texto:
        if 'a' <= char <= 'z':
            resultado.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            resultado.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
        elif '0' <= char <= '9':
            resultado.append(chr((ord(char) - ord('0') + shift) % 10 + ord('0')))
        else:
            resultado.append(char)
    return ''.join(resultado)

def decifrar_texto(texto_cifrado: str, shift: int = CHAVE_CESAR) -> str:
    """
    Decifra uma string revertendo a Cifra de César com deslocamento inverso (-shift).
    """
    if texto_cifrado is None:
        return None
    return cifrar_texto(texto_cifrado, -shift)

