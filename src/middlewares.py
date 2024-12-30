


import json
import logging
import time

from typing import Any, Dict, List, Tuple
from granian._granian import RSGIHTTPProtocol
from src import ASGI_RSGI_APP
from src.exceptions.http import HTTPException, InternalServerError
from src.utils import assure_tuples_of_str, get_protocol_args, headers_to_response, is_rsgi_app



class RequestLoggingMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.last = True
        self.parent = None

    async def exec(self, *args):

        scope, protocol_or_receive, send = get_protocol_args(args)
        mode = 'RSGI' if is_rsgi_app(scope) else 'ASGI'

        start_time = time.time()

        if is_rsgi_app(scope):

            protocol = protocol_or_receive

            await self.app.__rsgi__(scope, protocol)
        else:
            receive = protocol_or_receive
            assert receive
            assert send
            await self.app(scope, receive, send)

        duration = time.time() - start_time

        try:
            client = scope.client
        except:
            client = str(scope['client'])

        self.logger.info(f"Request {mode} processed in {duration:.4f} seconds from {client}")


class AuthenticationMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app
        self.last = True

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
            assert protocol_or_receive
            protocol = protocol_or_receive

            await self.app.__rsgi__(scope, protocol)
        else:
            receive = protocol_or_receive
            assert receive
            assert send
            await self.app(scope, receive, send)

    def __is_valid_token(self, token):
        return token == b"valid-token"
    

class HandleErrorMiddleware(ASGI_RSGI_APP):
    def __init__(self, app):
        self.app = app
        self.last = True
        self.parent = None

    async def exec(self, *args):
        protocol: RSGIHTTPProtocol
        scope, protocol_or_receive, send = get_protocol_args(args)

        try:
            if is_rsgi_app(scope):
                assert protocol_or_receive
                protocol = protocol_or_receive

                await self.app.__rsgi__(scope, protocol)
            else:
                receive = protocol_or_receive
                assert receive
                assert send
                await self.app(scope, receive, send)

        except HTTPException as error:
            response = error.json()

            if not is_rsgi_app(scope):
                scope['status'] = response["status"]

            if is_rsgi_app(scope):
                assert protocol_or_receive
                protocol = protocol_or_receive
                # assert isinstance(protocol, RSGIHTTPProtocol)
                response_headers = {'content-type': 'application/json'}
                headers_response = headers_to_response(response_headers, mode='str')
                protocol.response_str(
                    status=response['status'],
                    headers=assure_tuples_of_str(headers_response),
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
            # e = error
            # stacktrace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            # print(stacktrace)
            http_exception = InternalServerError(f"Internal Server Error: {error}")
            response = http_exception.json()

            if is_rsgi_app(scope):
                assert protocol_or_receive
                protocol = protocol_or_receive
                # assert isinstance(protocol, RSGIHTTPProtocol)
                response_headers = {'content-type': 'application/json'}
                response_headers.update(response.get('headers', {}))
                headers_response = headers_to_response(response_headers, mode='str')

                protocol.response_str(
                    status=response['status'],
                    headers=assure_tuples_of_str(headers_response),
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


class CORSMiddleware2(ASGI_RSGI_APP):

    def __init__(self, app: ASGI_RSGI_APP, whitelist=[]):
        self.app = app
        self.whitelist = whitelist
        self.last = True
        self.parent = None
        self.headers = {
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
            "access-control-allow-headers": "Content-Type, Authorization"
        }

    async def exec(self, *args):
        scope, protocol_or_receive, send = get_protocol_args(args)
        try:
            client = scope.client.split(':')[0]
        except Exception:
            client = scope['client'][0]

        original_response = await self._capture_response(
            scope,
            protocol_or_receive,
            send
        )

        for host in self.whitelist:
            if client in host:

                modified_headers: Dict[str, Any] = original_response["headers"]
                modified_headers.update(self.headers)
                break
        
        if is_rsgi_app(scope):
            await self.send_response(
                scope,
                protocol_or_receive,
                original_response["status"],
                original_response['body'],
                modified_headers
            )
            return

        else:
            await self.send_response(
                scope,
                send,
                original_response["status"],
                original_response["body"],
                modified_headers
            )
            return

    async def _capture_response(self, scope, protocol_or_receive, send):

        response_body = ''
        status = 200
        headers: List[Tuple[str, str]] = []

        class RSGICapture:

            def __init__(self, scope, protocol_or_receive, send) -> None:
                self.scope = scope
                self.protocol_or_receive = protocol_or_receive
                self.send = send

            async def __call__(self) -> Any:
                return await self.protocol_or_receive()


            async def send(self, *_, **kwargs):
                
                nonlocal status
                nonlocal headers
                nonlocal response_body

                status = int(kwargs['status'])
                headers = list(kwargs['headers'])
                response_body = str(kwargs['body'])
                

            def response_str(self, *_, **kwargs):

                nonlocal status
                nonlocal headers
                nonlocal response_body

                status = int(kwargs['status'])
                headers = list(kwargs['headers'])
                response_body = str(kwargs['body'])


        capture = RSGICapture(scope, protocol_or_receive, send)
        if is_rsgi_app(scope):
            # protocol = protocol_or_receive
            # assert isinstance(protocol, RSGIHTTPProtocol)
            await self.app.__rsgi__(scope, capture)
        else:
            receive = protocol_or_receive
            await self.app(scope, receive, capture.send)

        body = response_body.encode('utf-8')
        return {"status": status, "body": body.decode("utf-8"), "headers": self.headers}