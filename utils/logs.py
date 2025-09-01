# Simple logging - RU 4493981
from datetime import datetime

def log_info(message: str):
    print(f"[{datetime.utcnow().isoformat()}] INFO: {message}")
