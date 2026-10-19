import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from app.core.config import settings

password_hasher = PasswordHash.recommended()

ALGORITHM = "HS256"

def get_secret_key() -> str:
    secret_key = settings.SECRET_KEY

    if not secret_key:
        raise RuntimeError("SECRET_KEY is not configured.")

    return secret_key


def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password
    )

def create_access_token(user_id: int) -> str:
    expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM,
    )