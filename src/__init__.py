from __future__ import annotations
from abc import ABC
from contextlib import suppress
import logging
import json
import traceback

from typing import Any, Awaitable, Callable, Dict, List, Type, Union, Optional
from xmlrpc.client import boolean
from src.routes import UserRouter, TodosRouter
from src.exceptions.http import NotFoundError
from src.utils import assure_tuples_of_str, parse_query_string, is_rsgi_app, headers_to_response


Scope = Dict[str, Any]
Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]


with suppress(Exception):
    from granian.rsgi import Scope as GranianScope
    from granian._granian import RSGIHTTPProtocol


logging.basicConfig(level=logging.INFO)


class ASGI_RSGI_APP(ABC):

    last: boolean
    app: ASGI_RSGI_APP
    parent: Optional[ASGI_RSGI_APP]

    def __init__(self, *args) -> None:
        raise NotImplementedError

    def exec(self, *args):
        raise NotImplementedError

    def __str__(self):
        return f'{{ self.last: {self.last}, name: {self.__class__.__name__} }}'

    def __repr__(self):
        return f'{{ self.last: {self.last}, name: {self.__class__.__name__} }}'

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

        await self._send_response(scope, send, status, body, headers)

    async def _send_response(
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

            if send:
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

            print(self)

            try:
                params = {
                    "type": "http.response.start",
                    "status": status,
                    "headers": headers_response,
                }
                print(params)
                await send(params)
            except Exception:
                pass
            
            more_body = True
            if self.last:
                more_body = False

            params = {
                "type": "http.response.body",
                "body": body.encode('utf-8'),
                'more_body': more_body
            }
            await send(params)
            print(params)
            return
    
    def add_middleware(self, middleware: Type[ASGI_RSGI_APP], params=None) -> ASGI_RSGI_APP:

        self.last = True
        if params:
            self = middleware(self, params)
        else:
            self = middleware(self)

        self.app.last = False
        self.app.parent = self

        return self
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] == 'lifespan':
            return

        try:
            await self.exec(scope, receive, send)
        except:
            # traceback.print_exc()
            raise

    async def __rsgi__(self, scope, protocol):
        await self.exec(scope, protocol)


class App(ASGI_RSGI_APP):
    def __init__(self):

        self.last = True
        self.parent = None
        self.routers = (
            UserRouter(), TodosRouter()
        )

    async def __rsgi__(self, scope: 'GranianScope', protocol: 'RSGIHTTPProtocol'):

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


    async def __call__(self, scope: Scope, receive: Receive, send: Send):

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

    async def asgi_parse_body(
        self,
        receive: Receive
    ) -> Union[List[Any], Dict[str, Any], None]:

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

    async def rsgi_parse_body(
        self,
        protocol: 'RSGIHTTPProtocol'
    ) -> Union[List[Any], Dict[str, Any], None]:
        try:
            body_bytes = await protocol()
            body = json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            body = None
        
        return body