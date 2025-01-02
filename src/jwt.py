from datetime import datetime, timedelta
import json
import base64
import hmac
import hashlib
from typing import Optional

try:
    from src.config import settings
except:
    from config import settings


def base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode('utf-8')


def generate_jwt(
    payload: dict,
    secret_key: Optional[str] = None,
    expire_time_minutes = 60
) -> str:
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    if secret_key is None:
        raise AttributeError

    d = datetime.now() + timedelta(minutes=expire_time_minutes)

    payload['exp'] = d.timestamp()
    # Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = base64_url_encode(json.dumps(header).encode('utf-8'))

    # Payload
    payload_encoded = base64_url_encode(json.dumps(payload).encode('utf-8'))

    # Signature
    to_sign = f"{header_encoded}.{payload_encoded}".encode('utf-8')
    signature = hmac.new(secret_key.encode('utf-8'), to_sign, hashlib.sha256).digest()
    signature_encoded = base64_url_encode(signature)

    # Token
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

