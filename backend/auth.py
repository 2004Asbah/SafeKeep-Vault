from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import hashlib
from config import JWT_SECRET, JWT_ALGO

print("DEBUG: Loading auth module with fix v2")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # DEBUG: Print length to help diagnose 500 errors
    p_bytes = p.encode('utf-8')
    print(f"DEBUG_AUTH: Hashing password. Chars: {len(p)}, Bytes: {len(p_bytes)}")
    
    # Bcrypt has a 72-byte limit. We use a lower threshold (50) to be absolutely safe.
    # If password is long (or weird), we pre-hash it with SHA256 to get a fixed 64-char hex string.
    if len(p_bytes) > 50:
        print("DEBUG_AUTH: Password > 50 bytes. Pre-hashing with SHA256.")
        password_hash = hashlib.sha256(p_bytes).hexdigest()
        return pwd_context.hash(password_hash)
        
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    # Must match the hashing logic above
    p_bytes = p.encode('utf-8')
    
    if len(p_bytes) > 50:
        password_hash = hashlib.sha256(p_bytes).hexdigest()
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
