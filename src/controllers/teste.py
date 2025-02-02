from datetime import datetime
from src.models import Request
from src.domain.models import Consulta
from src.utils import (
    make_response,
    get, post,
)


class TesteController:

    url_prefix = "/teste/"

    @get("/")
    async def teste_endpoint_1(self, request: Request):
        consulta = Consulta(datetime(1,2,3, 0, 0, 0), 'motivo', 'medico')
        return make_response(consulta)

    @get("/<id:int>/")
    async def teste_endpoint_2(self, request: Request, id: int):
        return make_response({'id': id})

    @get("/<id_1:int>/teste/<id_2:int>/")
    async def teste_endpoint_3(self, request: Request, id_1: int, id_2: int):
        return make_response({'arg1': id_1, 'arg2': id_2})
    
    @get("/hello/<name:str>/")
    async def teste_endpoint_4(self, request: Request, name: str):
        return make_response({'name': name}, 200)

    @post("/login/<token:str>/")
    async def teste_endpoint_5(self, request: Request, token: str):
        body = await request.get_body()
        return make_response(
            {
                'token': token,
                'user_id': body.user_id,
                'query': request.query
            }
        )
