# Crypto helpers - RU 4493981
from cryptography.fernet import Fernet
import os

_key = os.getenv("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(_key)

def encrypt_text(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
