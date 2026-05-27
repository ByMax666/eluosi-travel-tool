"""
Authentication: password hashing (SHA-256 + salt) and JWT tokens.
Simple but secure enough for internal tool.
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

SECRET_KEY = "adu-travel-secret-key-change-in-production-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
SALT = b"adu_russia_travel_salt_2026"


def hash_password(password: str) -> str:
    """Hash password with PBKDF2-style approach using HMAC-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), SALT, 100000).hex()


def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(plain), hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None
