from asyncio import iscoroutinefunction
from datetime import datetime, timedelta
from functools import wraps
import json
import base64
import hmac
import hashlib
from typing import Callable, Optional

from src.exceptions.http import UnauthorizedError
from src.models import Request

try:
    from src.config import settings
except:
    from config import settings


def base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode('utf-8')


class JWTService:

    @staticmethod
    def generate(
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

    @staticmethod
    def decode(token: str, secret_key: Optional[str] = None) -> dict:
        if secret_key is None:
            secret_key = settings.SECRET_KEY
        if secret_key is None:
            raise AttributeError("Secret key is not provided.")

        try:
            # Dividir o token em partes
            header_encoded, payload_encoded, signature_encoded = token.split('.')

            # Decodificar e validar o header
            header = json.loads(base64.urlsafe_b64decode(header_encoded + "==").decode('utf-8'))
            if header.get("alg") != "HS256":
                raise ValueError("Unsupported algorithm")

            # Decodificar o payload
            payload = json.loads(base64.urlsafe_b64decode(payload_encoded + "==").decode('utf-8'))

            # Validar a assinatura
            to_sign = f"{header_encoded}.{payload_encoded}".encode('utf-8')
            expected_signature = hmac.new(secret_key.encode('utf-8'), to_sign, hashlib.sha256).digest()
            expected_signature_encoded = base64_url_encode(expected_signature)

            if not hmac.compare_digest(expected_signature_encoded, signature_encoded):
                raise ValueError("Invalid signature")

            # Verificar a expiração do token
            if 'exp' in payload:
                if datetime.now().timestamp() > payload['exp']:
                    raise ValueError("Token has expired")

            return payload
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid token: {e}")

