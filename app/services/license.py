import secrets
import hashlib
from datetime import datetime

def generate_license(product_id: int, email: str) -> str:
    raw = f"{product_id}:{email}:{secrets.token_hex(16)}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32].upper()
