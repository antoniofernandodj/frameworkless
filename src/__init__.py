

import json
from src.routes import UserRouter, TodosRouter
from src.exceptions.http import HTTPException, NotFoundError
from src.utils import parse_query_string


class App:
    def __init__(self):
        self.routers = (
            UserRouter(), TodosRouter()
        )

    async def __call__(self, scope, receive, send):
        try:
            query = parse_query_string(scope['query_string'].decode('utf-8'))
            handler, params = None, None
            for router in self.routers:
                handler, params = router.match_route(scope["method"], scope["path"])
                if handler is not None:
                    break

            if handler is None or params is None:
                raise NotFoundError("Route not Found")

            params.update(query)
            response = await handler(params, receive)
        except HTTPException as error:
            response = error.json()

        await self.send_response(send, response["status"], response.get("body", {}))


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


class SimpleLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # print(f"Handling request: {scope['method']} {scope['path']}")
        await self.app(scope, receive, send)
        
        # print("Request processed")
