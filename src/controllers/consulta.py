from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Consulta
from src.repository import ConsultaRepository
from src.exceptions.http import InternalServerError, NotFoundError, UnprocessableEntityError
from src.utils import (
    ParamsValidator,
    make_response,
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

    url_prefix: str = '/consultas/'

    def __init__(self, consulta_repository: ConsultaRepository) -> None:
        self.consulta_repository = consulta_repository

    @get("/")
    @validate_params(IdValidator)
    async def get_consulta(self, request: Request):
        consulta_id: int = request.query['id']
        consulta: Optional[Consulta] = self.consulta_repository.get_by_id(consulta_id)
        if consulta is None:
            raise NotFoundError('Consulta not found')
        return make_response(consulta)

    @post("/")    
    async def create_consulta(self, request: Request):
        body = await request.get_body(ConsultaFieldsValidator)
        consulta = Consulta(**body)  # type: ignore
        consulta: Consulta = self.consulta_repository.create(consulta)
        return make_response(consulta, 201)
    
    @patch("/<id:int>/marcar")
    @validate_params(IdValidator)
    async def marcar_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        consulta = self.consulta_repository.update(consulta_id, {'marcado': True})
        if consulta is None:
            raise NotFoundError('Consulta not found')
        return make_response(consulta)

    @put("/<id:int>")
    @validate_params(IdValidator)
    async def update_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        body = await request.get_body(ConsultaFieldsValidator)
        consulta: Optional[Consulta] = self.consulta_repository.update(consulta_id, body)
        if not consulta:
            raise NotFoundError("Consulta not found")
        return make_response(consulta)

    @delete("/<id:int>")
    @validate_params(IdValidator)
    async def delete_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        success: bool = self.consulta_repository.delete(consulta_id)
        if not success:
            raise NotFoundError("Consulta not found")
        return make_response(204)


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
