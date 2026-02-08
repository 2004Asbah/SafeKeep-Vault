
import sys
import os
import hashlib

# Mock config to avoid import errors
sys.modules['config'] = type('config', (), {'JWT_SECRET': 'secret', 'JWT_ALGO': 'HS256'})

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # Bcrypt has a 72-byte limit. For passwords that might exceed this,
    # we pre-hash with SHA256 to get a fixed-size input
    if len(p.encode('utf-8')) > 72:
        print(f"Password length {len(p.encode('utf-8'))} > 72 bytes. Hashing with SHA256 first.")
        # Use SHA256 to create a fixed-size hash, then hash that with bcrypt
        password_hash = hashlib.sha256(p.encode('utf-8')).hexdigest()
        print(f"SHA256 hash: {password_hash} (len: {len(password_hash)})")
        return pwd_context.hash(password_hash)
    return pwd_context.hash(p)

def test_long_password():
    print("Testing long password hashing...")
    long_pass = "a" * 100
    try:
        hashed = hash_password(long_pass)
        print(f"Success! Hashed password: {hashed[:20]}...")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_long_password()
