from pathlib import Path
import os
from dotenv import load_dotenv

# Mimic settings.py BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR: {BASE_DIR}")

# The fix I applied
env_path = BASE_DIR.parent / '.env'
print(f"Looking for .env at: {env_path}")

if env_path.exists():
    print(".env file FOUND.")
else:
    print(".env file NOT FOUND.")

load_dotenv(env_path)
smtp_pass = os.getenv('SMTP_PASS')
print(f"SMTP_PASS value: {smtp_pass}")
