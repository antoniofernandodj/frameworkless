


import logging
import time
from src import ASGI_APP
from src.exceptions.http import HTTPException, InternalServerError


class RequestLoggingMiddleware(ASGI_APP):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def __call__(self, scope, receive, send):
        start_time = time.time()

        await self.app(scope, receive, send)

        duration = time.time() - start_time

        self.logger.info(f"Request processed in {duration:.4f} seconds")


class AuthenticationMiddleware(ASGI_APP):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        authorization_header = dict(scope.get("headers", {})).get(b"authorization", None)
        if authorization_header is None:
            scope['current_user'] = None
        
        if self.is_valid_token(authorization_header):
            scope['current_user'] = 'John Doe'

        await self.app(scope, receive, send)

    def is_valid_token(self, token):
        return token == b"valid-token"
    

class HandleErrorMiddleware(ASGI_APP):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except HTTPException as error:
            response = error.json()
            scope['status'] = response["status"]
            await self.send_response(send, response["status"], response.get("body", {}))
        except Exception as error:
            http_exception = InternalServerError(f"Internal Server Error: {error}")
            response = http_exception.json()
            await self.send_response(send, response["status"], response["body"])


class CORSMiddleware(ASGI_APP):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = [
            (b"access-control-allow-origin", b"*"),
            (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
            (b"access-control-allow-headers", b"Content-Type, Authorization")
        ]
        scope["headers"] = dict(scope.get("headers", {}))
        scope["headers"].update(headers)

        await self.app(scope, receive, send)
