import os
import sys
from pathlib import Path
import boto3
from dotenv import load_dotenv

# 1. Load Environment Variables
env_path = Path(__file__).resolve().parent.parent / '.env'
print(f"📂 Looking for .env at: {env_path}")
load_dotenv(dotenv_path=env_path)

key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION", "eu-north-1")
bucket_name = os.getenv("S3_BUCKET_NAME")

required_vars = {
    "AWS_ACCESS_KEY_ID": key_id,
    "AWS_SECRET_ACCESS_KEY": secret_key,
    "S3_BUCKET_NAME": bucket_name
}

missing = [k for k, v in required_vars.items() if not v]

if missing:
    print(f"❌ Error: Missing environment variables: {', '.join(missing)}")
    print("Please verify your .env file has these keys defined.")
    sys.exit(1)

# 2. Initialize the S3 Client
s3 = boto3.client(
    's3',
    aws_access_key_id=key_id,
    aws_secret_access_key=secret_key,
    region_name=region
)

print(f"✅ .env Loaded! Found key ending in: ...{key_id[-4:] if key_id else 'None'}")

# 3. Perform the Upload Test
try:
    print(f"⏳ Attempting to upload test file to '{bucket_name}'...")
    s3.put_object(Bucket=bucket_name, Key='test_connection.txt', Body='Hello NGO Vault!')
    print("✅ Upload Success! Your app has full access to the new bucket.")

    # Cleanup
    s3.delete_object(Bucket=bucket_name, Key='test_connection.txt')
    print("✅ Cleanup Success! Permissions are verified.")

except Exception as e: # pylint: disable=broad-exception-caught
    print(f"❌ AWS Error: {e}")
