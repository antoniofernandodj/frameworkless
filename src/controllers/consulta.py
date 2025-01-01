from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Consulta
from src.repository import ConsultaRepository
from src.exceptions.http import InternalServerError, NotFoundError
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, patch, delete
)


class ConsultaFieldsValidator(ParamsValidator):
    data: Annotated[str, "Invalid consulta payload"]
    medico: Annotated[str, "Invalid consulta payload"]
    especialidade: Annotated[str, "Invalid consulta payload"]
    local: Annotated[str, "Invalid consulta payload"]
    observacoes: Annotated[str, "Invalid consulta payload"]
    paciente_id: Annotated[str, "Invalid consulta payload"]
    doenca_id: Annotated[str, "Invalid consulta payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class ConsultaController:
    def __init__(self, consulta_repository: ConsultaRepository) -> None:
        self.consulta_repository = consulta_repository

    @get(r"^/consultas/$")
    @validate_params(IdValidator)
    async def get_consulta(self, request: Request):
        consulta_id: int = request.query['id']
        consulta: Optional[Consulta] = self.consulta_repository.get_by_id(consulta_id)
        if consulta is None:
            raise LookupError('consulta not found')

        return make_response(consulta)

    @post(r"^/consultas/$")    
    @validate_body(ConsultaFieldsValidator)
    async def create_consulta(self, request: Request):
        body = await request.get_body()
        consulta: Consulta = self.consulta_repository.create(body['description'])
        return make_response(consulta, 201)
    
    @patch(r"^/consultas/(?P<id>\d+)/marcar$")
    @validate_params(IdValidator)
    async def marcar_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        consulta = self.consulta_repository.update(consulta_id, {'marcado': True})
        if consulta is None:
            raise LookupError('consulta not found')

        return make_response(consulta)

    @put(r"^/consultas/(?P<id>\d+)$")
    @validate_body(ConsultaFieldsValidator)
    @validate_params(IdValidator)
    async def update_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        body = await request.get_body()
        consulta: Optional[Consulta] = self.consulta_repository.update(consulta_id, body)
        if not consulta:
            raise LookupError("consulta not found")

        return make_response(consulta)

    @delete(r"^/consultas/(?P<id>\d+)$")
    @validate_params(IdValidator)
    async def delete_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        success: bool = self.consulta_repository.delete(consulta_id)
        if not success:
            raise LookupError("consulta not found")

        return make_response({})


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
