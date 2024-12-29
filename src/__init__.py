from __future__ import annotations
import logging
import time
import json
from typing import Type
from src.routes import UserRouter, TodosRouter
from src.exceptions.http import HTTPException, NotFoundError
from src.utils import parse_query_string


logging.basicConfig(level=logging.INFO)



class ASGI_APP:
    async def send_response(self, send, status, body):
        headers = [[b'content-type', b'application/json']]
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": headers,
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps(body).encode(),
        })

    
    def add_middleware(self, middleware: Type) -> ASGI_APP:
        self = middleware(self)
        return self


class App(ASGI_APP):
    def __init__(self):
        self.routers = (
            UserRouter(), TodosRouter()
        )

    async def __call__(self, scope, receive, send):

        query = parse_query_string(scope['query_string'].decode('utf-8'))
        endpoint_handler, params = None, None
        for router in self.routers:
            endpoint_handler, params = router.match_route(
                scope["method"], scope["path"]
            )
            if endpoint_handler is not None:
                break
        if endpoint_handler is None or params is None:
            raise NotFoundError("Route not Found")

        params.update(query)
        response = await endpoint_handler(params, receive)
        scope['status'] = response["status"]
        await self.send_response(send, response["status"], response.get("body", {}))

