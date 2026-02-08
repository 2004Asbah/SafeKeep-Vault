from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import hashlib
from config import JWT_SECRET, JWT_ALGO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # Bcrypt has a 72-byte limit. For passwords that might exceed this,
    # we pre-hash with SHA256 to get a fixed-size input
    if len(p.encode('utf-8')) > 72:
        # Use SHA256 to create a fixed-size hash, then hash that with bcrypt
        password_hash = hashlib.sha256(p.encode('utf-8')).hexdigest()
        return pwd_context.hash(password_hash)
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    # Match the hashing behavior
    if len(p.encode('utf-8')) > 72:
        password_hash = hashlib.sha256(p.encode('utf-8')).hexdigest()
        return pwd_context.verify(password_hash, hashed)
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
