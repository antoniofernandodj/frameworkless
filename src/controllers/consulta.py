from datetime import datetime
from src.models import Request
from typing import Annotated, Optional
from src.domain.models import Consulta
from src.repository import ConsultaRepository
from src.exceptions.http import NotFoundError
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, post, put, patch, delete
)


class ConsultaFieldsValidator(ParamsValidator):
    horario: Annotated[str, "`horario` required"]
    motivo: Annotated[str, "`motivo` required"]
    medico: Annotated[str, "`medico` required"]
    especialidade: Annotated[str, "`especialidade` required"]
    local: Annotated[str, "`local` required"]
    observacoes: Annotated[str, "`observacoes` required"]
    paciente_id: Annotated[str, "`paciente_id` required"]
    doenca_id: Annotated[str, "`doenca_id` required"]


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
        body.horario = datetime.fromisoformat(body.pop('horario'))
        consulta = Consulta(**body)  # type: ignore
        consulta: Consulta = self.consulta_repository.create(consulta)
        return make_response(consulta, 201)
    
    @patch("/<id:int>/marcar")
    async def marcar_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        body = request.get_body()
        marcado = (getattr(body, 'marcar', None) or True) if body else True
        consulta = self.consulta_repository.update(consulta_id, {
            'marcado': marcado
        })
        if consulta is None:
            raise NotFoundError('Consulta not found')
        return make_response(consulta)

    @put("/<id:int>")
    async def update_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        body = await request.get_body(ConsultaFieldsValidator)
        consulta: Optional[Consulta] = self.consulta_repository.update(consulta_id, body)
        if not consulta:
            raise NotFoundError("Consulta not found")
        return make_response(consulta)

    @delete("/<id:int>")
    async def delete_consulta(self, request: Request, id: int):
        consulta_id = int(id)
        success: bool = self.consulta_repository.delete(consulta_id)
        if not success:
            raise NotFoundError("Consulta not found")
        return make_response(204)
