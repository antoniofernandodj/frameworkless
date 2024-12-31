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

    @get(r"^/teste/$")
    async def teste_endpoint_1(self, request: Request):
        print('request: ', request)
        return make_response(200, {})


    @post(r"^/teste/$")
    async def teste_endpoint_2(self, request: Request):
        print('request: ', request)
        print('Fetching the body...')
        print({'/teste/ body': await request.get_body()})

        print(f'request headers: {request.headers}')

        return make_response(200, {})
    

    @patch(r"^/teste/(?P<id>\d+)/sub$")
    async def teste_endpoint_3(self, request: Request):
        print(f'request: {request}')
        return make_response(200, {})


    @put(r"^/teste/(?P<id>\d+)$")
    async def teste_endpoint_4(self, request: Request):
        print(f'request: {request}')
        return make_response(200, {})


    @delete(r"^/teste/(?P<id>\d+)$")
    async def teste_endpoint_5(self, request: Request):
        print(f'request: {request}')
        return make_response(200, {})


"""
class Consulta(DomainModel):
    def __init__(
        self,
        id: int,
        data: date,
        medico: str,
        especialidade: Optional[str] = None,
        local: Optional[str] = None,
        observacoes: Optional[str] = None,
        paciente_id: Optional[int] = None,
        doenca_id: Optional[int] = None
    ):
        self.id = id
        self.data = data
        self.medico = medico
        self.especialidade = especialidade
        self.local = local
        self.observacoes = observacoes
        self.paciente_id = paciente_id
        self.doenca_id = doenca_id

"""
