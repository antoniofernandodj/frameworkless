from __future__ import annotations

from abc import ABC
from asyncio import iscoroutinefunction
from contextlib import suppress
import inspect
import logging
import json
from src import types as t

from typing import Any, Callable, Coroutine, Dict, List, Type, Union, Optional
from src.models import Request
from src.routers import (
    ConsultaRouter,
    DoencaRouter,
    ExameRouter,
    MedicamentoRouter,
    PacienteRouter,
    TarefaRouter,
    TesteRouter
)

from src.exceptions.http import NotFoundError
from src.utils import Response, assure_tuples_of_str, parse_query_string, is_rsgi_app, headers_to_response


with suppress(Exception):
    from granian.rsgi import Scope as GranianScope
    from granian._granian import RSGIHTTPProtocol


logging.basicConfig(level=logging.INFO)


class ASGI_RSGI_APP(ABC):

    last: bool
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
            response_headers = {}
            response_headers.update(headers)
            headers_response = headers_to_response(response_headers, mode='str')
            send.response_str(
                status=status,
                headers=assure_tuples_of_str(headers_response),
                body=body
            )

        else:
            response_headers = {}
            response_headers.update(headers)
            headers_response = headers_to_response(
                response_headers, mode='bytes'
            )

            print(f'Self: {self}')

            try:
                params = {
                    "type": "http.response.start",
                    "status": status,
                    "headers": headers_response,
                }
                print(f"params: {params}")
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
            print(f"params: {params}")
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
    
    async def __call__(self, scope: t.Scope, receive: t.Receive, send: t.Send):
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

        from src.infra.database.sql import SessionLocal
        # from src.infra.database.mongo import client

        self.last = True
        self.parent = None

        session = SessionLocal()
        # session = client

        self.routers = (
            ConsultaRouter(session),
            DoencaRouter(session),
            ExameRouter(session),
            MedicamentoRouter(session),
            TarefaRouter(session),
            PacienteRouter(session),
            TesteRouter(),
        )

    async def __rsgi__(self, scope: 'GranianScope', protocol: 'RSGIHTTPProtocol'):

        async def get_body():
            return await self.rsgi_parse_body(protocol)

        response = await self.dispatch_request(
            scope.query_string,
            scope.path,
            scope.method,
            get_body,
            dict(scope.headers.items())
        )

        await self.send_response(
            scope,
            protocol,
            response.status,
            json.dumps(response.body),
            response.headers
        )

    async def __call__(self, scope: t.Scope, receive: t.Receive, send: t.Send):

        if scope['type'] == 'lifespan':
            return
        
        async def get_body():
            return await self.asgi_parse_body(receive)
        
        headers = {
            key.decode('utf-8'): item.decode('utf-8')
            for key, item in dict(scope['headers']).items()
        }

        response = await self.dispatch_request(
            scope['query_string'].decode('utf-8'),
            scope['path'],
            scope['method'],
            get_body,
            headers
        )
        scope['status'] = response.status

        await self.send_response(
            scope,
            send,
            scope['status'],
            json.dumps(response.body),
            response.headers
        )

    async def dispatch_request(
        self,
        query_string: str,
        path: str,
        method: str,
        get_body_callback: Callable[[], Coroutine],
        headers: Dict[str, str],
    ) -> Response:
        query = parse_query_string(query_string)
        endpoint_handler, path_args = None, None
        for router in self.routers:
            endpoint_handler, path_args = router.match_route(method, path)
            if endpoint_handler is not None:
                break

        if endpoint_handler is None or path_args is None:
            raise NotFoundError("Route not Found")

        response: Response
        request = Request(query, get_body_callback, headers)

        for param_name, param_type in endpoint_handler.__annotations__.items():
            for arg_name, arg_value in path_args.items():
                if param_name == arg_name:
                    path_args[arg_name] = param_type(arg_value)

        if iscoroutinefunction(endpoint_handler):
            response = await endpoint_handler(request, **path_args)
        else:
            response = endpoint_handler(request, **path_args)
            print(response)

        return response

    async def asgi_parse_body(
        self,
        receive: t.Receive
    ) -> Union[List[Any], Dict[str, Any], str, None]:

        body_bytes = b""
        try:
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body_bytes += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
        except Exception:
            return None

        try:
            body = json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            try:
                body = body_bytes.decode('utf-8')
            except:
                body = str(body_bytes)
        
        return body

    async def rsgi_parse_body(
        self,
        protocol: 'RSGIHTTPProtocol'
    ) -> Union[List[Any], Dict[str, Any], str, None]:
        
        try:
            body_bytes = await protocol()
        except:
            return None

        try:
            body = json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            try:
                body = body_bytes.decode('utf-8')
            except:
                body = str(body_bytes)
        
        return body