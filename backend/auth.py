from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET, JWT_ALGO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def decode_token(token: str) -> str:
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    return data["sub"]
