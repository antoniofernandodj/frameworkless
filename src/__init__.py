from __future__ import annotations
from abc import ABC
import logging
import time
import json
import traceback

from typing import Any, Coroutine, Dict, List, Type, Union
from src.routes import UserRouter, TodosRouter
from src.exceptions.http import NotFoundError
from src.utils import assure_tuples_of_str, parse_query_string, is_rsgi_app, headers_to_response

try:
    from granian.rsgi import Scope
    from granian._granian import RSGIHTTPProtocol
except:
    pass


logging.basicConfig(level=logging.INFO)



class ASGI_RSGI_APP(ABC):

    def exec(self, *args):
        raise NotImplementedError

    def get_headers_from_scope(self, scope):
        try:
            return scope.get('headers')
        except:
            try:
                return getattr(scope, 'headers', None) or {}
            except:
                return {}

    async def send_response(
        self,
        scope: Any,
        send: Any,
        status: int,
        body: str,
        headers: dict
    ):

        if is_rsgi_app(scope):

            response_headers = {'content-type': 'application/json'}
            response_headers.update(headers)
            headers_response = headers_to_response(response_headers, mode='str')

            send.response_str(
                status=status,
                headers=assure_tuples_of_str(headers_response),
                body=body
            )

        else:
            response_headers = {'content-type': 'application/json'}
            response_headers.update(headers)
            headers_response = headers_to_response(
                response_headers, mode='bytes'
            )

            await send({
                "type": "http.response.start",
                "status": status,
                "headers": headers_response,
            })
            await send({
                "type": "http.response.body",
                "body": body.encode('utf-8'),
            })


    
    def add_middleware(self, middleware: Type) -> ASGI_RSGI_APP:
        self = middleware(self)
        return self
    
    async def __call__(self, scope: Any, receive: Coroutine, send: Any):
        if scope['type'] == 'lifespan':
            return

        try:
            await self.exec(scope, receive, send)
        except:
            print(traceback.print_exc())
            raise

    async def __rsgi__(self, scope, protocol):
        await self.exec(scope, protocol)


class App(ASGI_RSGI_APP):
    def __init__(self):
        self.routers = (
            UserRouter(), TodosRouter()
        )

    async def __rsgi__(self, scope: 'Scope', protocol: 'RSGIHTTPProtocol'):

        response = await self.dispatch_request(
            scope.query_string,
            scope.path,
            scope.method,
            await self.rsgi_parse_body(protocol)
        )

        await self.send_response(
            scope,
            protocol,
            response["status"],
            json.dumps(response.get('body', {})),
            response.get('headers', {})
        )


    async def __call__(self, scope, receive, send):

        if scope['type'] == 'lifespan':
            return

        response = await self.dispatch_request(
            scope['query_string'].decode('utf-8'),
            scope['path'],
            scope['method'],
            await self.asgi_parse_body(receive)
        )
        scope['status'] = response["status"]

        await self.send_response(
            scope,
            send,
            scope['status'],
            json.dumps(response.get("body", {})),
            response.get('headers', {})
        )

    async def dispatch_request(
        self,
        query_string: str,
        path: str,
        method: str,
        body: Any
    ):
        query = parse_query_string(query_string)
        endpoint_handler, params = None, None
        for router in self.routers:
            endpoint_handler, params = router.match_route(method, path)
            if endpoint_handler is not None:
                break
        if endpoint_handler is None or params is None:
            raise NotFoundError("Route not Found")

        params.update(query)
        return await endpoint_handler(params, body)

    async def asgi_parse_body(self, receive) -> Union[List[Any], Dict[str, Any], None]:
        try:
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break

            return json.loads(body.decode("utf-8") or "{}")
        except Exception:
            return None

    async def rsgi_parse_body(self, protocol):
        try:
            body_bytes = await protocol()
            body = json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            body = None
        
        return body