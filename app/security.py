import secrets

import bcrypt
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

_BCRYPT_MAX_BYTES = 72


def hash_request_password(raw_password: str) -> str:
    password_bytes = raw_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_request_password(raw_password: str, hashed: str) -> bool:
    password_bytes = raw_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))


_fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def generate_real_password(length: int = 24) -> str:
    return secrets.token_urlsafe(length)


def encrypt_real_password(raw_password: str) -> str:
    return _fernet.encrypt(raw_password.encode()).decode()


def decrypt_real_password(encrypted_password: str) -> str:
    try:
        return _fernet.decrypt(encrypted_password.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Не удалось расшифровать пароль — проверь ENCRYPTION_KEY") from exc
