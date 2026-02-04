from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from config import JWT_SECRET, JWT_ALGO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # Bcrypt has a 72-byte limit, truncate by bytes if necessary
    password_bytes = p.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes)

def verify_password(p: str, hashed: str) -> bool:
    # Truncate to match hash_password behavior
    password_bytes = p.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes, hashed)

def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def decode_token(token: str) -> str:
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    return data["sub"]
