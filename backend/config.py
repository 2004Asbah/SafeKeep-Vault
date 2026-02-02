import os

# --- AWS Secrets Manager Integration ---
try:
    from aws_secrets import get_secret
except ImportError:
    # Fallback if aws_secrets.py is missing or dependencies fail
    def get_secret(*args, **kwargs): return None

AWS_SECRET_NAME = os.getenv("AWS_SECRET_NAME")
_secrets = {}

if AWS_SECRET_NAME:
    print(f"Loading configuration from AWS Secrets Manager: {AWS_SECRET_NAME}")
    _fetched = get_secret(AWS_SECRET_NAME)
    if _fetched:
        _secrets = _fetched
    else:
        print("Warning: Failed to fetch secrets, falling back to environment variables.")

# --- Configuration Variables ---
# Priority: Secrets Manager > Environment Variables > Defaults

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_BUCKET_NAME = _secrets.get("S3_BUCKET_NAME", os.getenv("S3_BUCKET_NAME"))

# Database (optional for now)
DATABASE_URL = _secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///./safekeep.db"))

JWT_SECRET = _secrets.get("JWT_SECRET", os.getenv("JWT_SECRET", "CHANGE_ME_SUPER_SECRET"))
JWT_ALGO = "HS256"
