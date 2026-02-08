from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import hashlib
from config import JWT_SECRET, JWT_ALGO

print("DEBUG: Loading auth module with fix v3 - always prehash")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash(password: str) -> str:
    """
    Always SHA256 prehash passwords before bcrypt.
    
    This is a common security pattern that:
    1. Completely eliminates bcrypt's 72-byte limitation
    2. Normalizes all passwords to exactly 64 hex characters
    3. Is used by many production systems (e.g., Dropbox)
    
    Note: We use SHA256 hex digest (64 chars) which is safely under bcrypt's limit.
    """
    password_bytes = password.encode('utf-8')
    return hashlib.sha256(password_bytes).hexdigest()


def hash_password(p: str) -> str:
    """Hash a password using SHA256 + bcrypt."""
    prehashed = _prehash(p)
    return pwd_context.hash(prehashed)


def verify_password(p: str, hashed: str) -> bool:
    """Verify a password against a stored hash."""
    prehashed = _prehash(p)
    try:
        return pwd_context.verify(prehashed, hashed)
    except Exception:
        # Handle any bcrypt verification errors gracefully
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

