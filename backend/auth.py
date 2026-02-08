from datetime import datetime, timedelta
import jwt
import hashlib
import base64
import bcrypt
from config import JWT_SECRET, JWT_ALGO

print("DEBUG: Loading auth module with fix v4 - direct bcrypt")


def _prehash(password: str) -> bytes:
    """
    SHA256 prehash + base64 encode for bcrypt compatibility.
    
    This approach:
    1. Hashes password with SHA256 (32 bytes raw)
    2. Base64 encodes to get ASCII-safe string (44 chars)
    3. Returns as bytes for bcrypt
    
    The result is always exactly 44 bytes, well under bcrypt's 72-byte limit.
    """
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256(password_bytes).digest()  # 32 bytes
    b64_encoded = base64.b64encode(sha256_hash)  # 44 bytes
    return b64_encoded


def hash_password(password: str) -> str:
    """Hash a password using SHA256 + bcrypt."""
    prehashed = _prehash(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        prehashed = _prehash(password)
        stored_hash_bytes = stored_hash.encode('utf-8')
        return bcrypt.checkpw(prehashed, stored_hash_bytes)
    except Exception:
        return False


def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> str:
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    return data["sub"]


