"""Hashing and password-strength checks for employee login credentials."""

import hashlib
import hmac
import secrets


PBKDF2_ITERATIONS = 310_000
COMMON_PASSWORDS = {
    "12345678", "123456789", "password", "senha123", "qwerty123",
    "admin123", "batata123", "abc12345",
}


def _longest_sequential_run(password: str) -> int:
    """Search every sequential run with recursive depth-first backtracking."""
    longest = 1 if password else 0

    def explore(index: int, step: int, path: list[str]) -> None:
        nonlocal longest
        longest = max(longest, len(path))
        if index >= len(password):
            return
        current_step = ord(password[index]) - ord(password[index - 1])
        if current_step == step and current_step in (-1, 1):
            path.append(password[index])
            explore(index + 1, step, path)
            path.pop()

    for start in range(len(password)):
        for step in (-1, 1):
            explore(start + 1, step, [password[start]])
    return longest


def avaliar_forca_senha(password: str) -> tuple[str, str]:
    """Return (weak/medium/strong classification, reason) for a password."""
    value = password or ""
    if len(value) > 256:
        return "Fraca", "A senha não pode ultrapassar 256 caracteres."
    normalized = value.lower()
    categories = sum((
        any(char.islower() for char in value),
        any(char.isupper() for char in value),
        any(char.isdigit() for char in value),
        any(not char.isalnum() for char in value),
    ))
    sequential_run = _longest_sequential_run(normalized)
    repeated_block = any(
        normalized[index:index + size] == normalized[index + size:index + 2 * size]
        for index in range(len(normalized))
        for size in range(1, (len(normalized) - index) // 2 + 1)
    )

    if normalized in COMMON_PASSWORDS:
        return "Fraca", "Senha comum e fácil de adivinhar."
    if len(value) < 8:
        return "Fraca", "Use pelo menos 8 caracteres."
    if sequential_run >= 4 or repeated_block:
        return "Fraca", "Evite sequências ou blocos repetidos."
    if categories < 3 or len(set(value)) < 6:
        return "Fraca", "Misture letras maiúsculas, minúsculas, números e símbolos."
    if len(value) < 12 or categories < 4 or sequential_run >= 3:
        return "Média", "Senha aceitável; aumente o tamanho ou a variedade para fortalecê-la."
    return "Forte", "Boa combinação de tamanho e variedade."


def gerar_credencial(password: str) -> tuple[str, str]:
    """Create a salted PBKDF2-SHA256 credential; never store plaintext."""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return password_hash.hex(), salt.hex()


def verificar_senha(password: str, password_hash: str, salt_hex: str) -> bool:
    """Constant-time comparison against a previously generated credential."""
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(password_hash)
    except (TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(actual, expected)
