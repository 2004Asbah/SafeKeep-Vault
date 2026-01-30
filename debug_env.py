from dotenv import dotenv_values
from pathlib import Path

env_path = Path('.env').resolve()
print(f"Reading from: {env_path}")

if not env_path.exists():
    print("❌ .env file NOT found!")
else:
    config = dotenv_values(env_path)
    print(f"Found {len(config)} keys:")
    for key in config.keys():
        print(f" - {key}")
