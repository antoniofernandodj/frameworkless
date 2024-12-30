


import json
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple
from src import ASGI_RSGI_APP
from src.exceptions.http import HTTPException, InternalServerError
from src.utils import get_protocol_args, headers_to_response, is_rsgi_app




class RequestLoggingMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def exec(self, *args):

        scope, protocol_or_receive, send = get_protocol_args(args)
        mode = 'RSGI' if is_rsgi_app(scope) else 'ASGI'

        start_time = time.time()

        if is_rsgi_app(scope):
            protocol = protocol_or_receive
            await self.app.__rsgi__(scope, protocol)
        else:
            receive = protocol_or_receive
            await self.app(scope, receive, send)

        duration = time.time() - start_time

        self.logger.info(f"Request {mode} processed in {duration:.4f} seconds")


class AuthenticationMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app

    async def exec(self, *args):
        scope, protocol_or_receive, send = get_protocol_args(args)

        headers = self.get_headers_from_scope(scope)
        authorization_header = dict(headers).get(b"authorization", None)
        if authorization_header is None:
            try:
                scope['current_user'] = None
            except:
                pass
                # scope.current_user = None
        
        if self.__is_valid_token(authorization_header):
            try:
                scope['current_user'] = 'John Doe'
            except:
                pass
                # scope.current_user = 'John Doe'

        if is_rsgi_app(scope):
            protocol = protocol_or_receive
            await self.app.__rsgi__(scope, protocol)
        else:
            receive = protocol_or_receive
            await self.app(scope, receive, send)

    def __is_valid_token(self, token):
        return token == b"valid-token"
    

class HandleErrorMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app

    async def exec(self, *args):
        scope, protocol_or_receive, send = get_protocol_args(args)

        try:
            if is_rsgi_app(scope):
                protocol = protocol_or_receive
                await self.app.__rsgi__(scope, protocol)
            else:
                receive = protocol_or_receive
                await self.app(scope, receive, send)

        except HTTPException as error:
            response = error.json()
            
            if not is_rsgi_app(scope):
                scope['status'] = response["status"]

            if is_rsgi_app(scope):
                if not protocol:
                    raise RuntimeError
                response_headers = {'content-type': 'application/json'}
                headers_response = headers_to_response(response_headers, mode='str')
                protocol.response_str(
                    status=response['status'],
                    headers=headers_response,
                    body=json.dumps(response['body'])
                )
            else:
                body = response.get("body", {})
                await self.send_response(
                    scope,
                    send,
                    response["status"],
                    json.dumps(body),
                    response.get('headers', {})
                )

        except Exception as error:
            e = error
            stacktrace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            print(stacktrace)
            http_exception = InternalServerError(f"Internal Server Error: {error}")
            response = http_exception.json()

            if is_rsgi_app(scope):
                if not protocol:
                    raise RuntimeError

                response_headers = {'content-type': 'application/json'}
                response_headers.update(response.get('headers', {}))
                headers_response = headers_to_response(response_headers, mode='str')

                protocol.response_str(
                    status=response['status'],
                    headers=headers_response,
                    body=json.dumps(response['body'])
                )
            else:
                body = response.get("body", {})
                await self.send_response(
                    scope,
                    send,
                    response["status"],
                    json.dumps(body),
                    response.get('headers', {})
                )


# TODO
class CORSMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app

    async def exec(self, *args,):

        scope, protocol_or_receive, send = get_protocol_args(args)

        headers = [
            (b"access-control-allow-origin", b"*"),
            (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
            (b"access-control-allow-headers", b"Content-Type, Authorization")
        ]

        try:
            scope["headers"] = dict(self.get_headers_from_scope(scope))
            scope["headers"].update(headers)
        except Exception:
            pass

        if is_rsgi_app(scope):
            protocol = protocol_or_receive
            await self.app.__rsgi__(scope, protocol)
        else:
            receive = protocol_or_receive
            await self.app(scope, receive, send)
