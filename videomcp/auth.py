from __future__ import annotations

import getpass
import os
from pathlib import Path

import bcrypt

ALLOWED_EMAIL = os.getenv("VIDEOMCP_ALLOWED_EMAIL", "marugaul@gmail.com").strip().lower()
PASSWORD_HASH = os.getenv("VIDEOMCP_PASSWORD_HASH", "")
SESSION_SECRET = os.getenv("VIDEOMCP_SESSION_SECRET", "")


def verify_login(email: str, password: str) -> bool:
    if email.strip().lower() != ALLOWED_EMAIL:
        return False
    if not PASSWORD_HASH:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), PASSWORD_HASH.encode("utf-8"))
    except ValueError:
        return False


def main():
    password = getpass.getpass("Nueva clave para VideoMCP: ")
    confirm = getpass.getpass("Repetir clave: ")
    if not password or password != confirm:
        raise SystemExit("Las claves no coinciden o están vacías.")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    secret = os.urandom(32).hex()
    print("\nAgregá estas líneas a tu archivo .env:\n")
    print(f"VIDEOMCP_ALLOWED_EMAIL={ALLOWED_EMAIL}")
    print(f"VIDEOMCP_PASSWORD_HASH={hashed}")
    print(f"VIDEOMCP_SESSION_SECRET={secret}")
