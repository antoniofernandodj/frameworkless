from datetime import date
from src.exceptions.http import UnprocessableEntityError
from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Consulta
from src.domain.services.consulta import ConsultaService
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, patch, delete
)


class TesteController:

    @get("/teste/")
    async def teste_endpoint_1(self, request: Request):
        consulta = Consulta(date(1,2,3), True, 'medico')
        return make_response(consulta)

    @get("/teste/<id:int>/")
    async def teste_endpoint_2(self, request: Request, id: int):
        return make_response({'id': id})

    @get("/teste/<id_1:int>/teste/<id_2:int>/")
    async def teste_endpoint_3(self, request: Request, id_1: int, id_2: int):
        return make_response({'arg1': id_1, 'arg2': id_2})
    
    @get("/hello/<name:str>/")
    async def teste_endpoint_4(self, request: Request, name: str):
        return make_response({'name': name}, 200)

    @post("/test/login/<token:str>/")
    async def teste_endpoint_5(self, request: Request, token: str):

        body = await request.get_body(None)
        if body is None:
            raise UnprocessableEntityError

        return make_response(
            {
                'token': token,
                'user_id': body.user_id,
                'query': request.query
            }
        )
