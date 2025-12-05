# app/auth/jwt_handler.py

from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "testsecretkey123"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    """Real token generator (tests override this)"""
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str):
    """Real decoder (tests override this)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
