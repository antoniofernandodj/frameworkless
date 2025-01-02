from __future__ import annotations

from abc import ABC
from asyncio import iscoroutinefunction
from contextlib import suppress
import inspect
import logging
import json
from src import _types as t

try:
    from config import settings
except:
    from src.config import settings

from typing import Any, Callable, Coroutine, Dict, List, Type, Union, Optional
from src.models import DotDict, Request
from src.routers import (
    ConsultaRouter,
    DoencaRouter,
    ExameRouter,
    MedicamentoRouter,
    PacienteRouter,
    TarefaRouter,
    TesteRouter,
    AuthRouter
)

from src.exceptions.http import NotFoundError, UnprocessableEntityError
from src.utils import ParamsValidator, assure_tuples_of_str, parse_query_string, is_rsgi_app, headers_to_response
from src.models import Response


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
    def __init__(self, mode: str = 'dev'):

        print(f'Running in mode: {mode}')
        self.last = True
        self.parent = None
        self.mode = mode
        settings.set_mode(mode)

        from src.infra.database.sql import init_mappers
        from src.infra.database.sql import get_session_local
        # from src.infra.database.mongo import client

        SessionLocal = get_session_local()
        session = SessionLocal()
        # session = client

        init_mappers()

        self.routers = (
            # ConsultaRouter(session),
            # DoencaRouter(session),
            # ExameRouter(session),
            # MedicamentoRouter(session),
            # TarefaRouter(session),
            # PacienteRouter(session),
            TesteRouter(),
            AuthRouter(session),
        )

    async def __rsgi__(self, scope: 'GranianScope', protocol: 'RSGIHTTPProtocol'):

        async def get_body(validator: Optional[Type[ParamsValidator]] = None):
            request_body = await self.rsgi_parse_body(protocol)

            if validator is None:
                return request_body

            if validator is None and not request_body:
                return None

            if not isinstance(request_body, DotDict):
                raise UnprocessableEntityError('Tipo de body incorreto')

            request_body = validator.validate(request_body)
            return request_body

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
        
        async def get_body(validator: Optional[Type[ParamsValidator]] = None):
            request_body = await self.asgi_parse_body(receive)
            if validator is None:
                return request_body

            if validator is None and not request_body:
                return None

            if not isinstance(request_body, DotDict):
                raise UnprocessableEntityError('Tipo de body incorreto')

            request_body = validator.validate(request_body)
            return request_body
        
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
        get_body_callback: Callable[
            [Optional[Type[ParamsValidator]]],
            Coroutine[Any, Any, Optional[DotDict]]
        ],
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
            print({
                'request': request,
                'response': response,
                'endpoint_handler': endpoint_handler
            })
        else:
            response = endpoint_handler(request, **path_args)

        return response

    async def asgi_parse_body(
        self,
        receive: t.Receive
    ) -> Optional[DotDict]:

        body_bytes = b""
        try:
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body_bytes += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
        except Exception:
            raise UnprocessableEntityError
        
        if not body_bytes:
            return None

        try:
            body = json.loads(body_bytes.decode('utf-8'))
            body = DotDict(body)
        except json.JSONDecodeError:
            raise UnprocessableEntityError

        return body

    async def rsgi_parse_body(
        self,
        protocol: 'RSGIHTTPProtocol'
    ) -> Optional[DotDict]:

        body_bytes: bytes = await protocol()
        if not body_bytes:
            return None
        
        body_string = body_bytes.decode('utf-8')

        try:
            body = json.loads(body_string)
            body = DotDict(body)
        except json.JSONDecodeError:
            raise UnprocessableEntityError
        
        return body