from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Exame
from src.repository import ExameRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, patch, delete
)


class ExameFieldsValidator(ParamsValidator):
    tipo: Annotated[str, "Invalid exame payload"]
    data: Annotated[str, "Invalid exame payload"]
    laboratorio: Annotated[str, "Invalid exame payload"]
    consulta: Annotated[str, "Invalid exame payload"]
    paciente: Annotated[str, "Invalid exame payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class ExameController:
    def __init__(self, exame_repository: ExameRepository) -> None:
        self.exame_repository = exame_repository

    @get(r"^/exames/$")
    @validate_params(IdValidator)
    async def get_exame(self, request: Request):
        exame_id: int = request.query['id']
        exame: Optional[Exame] = self.exame_repository.get_by_id(exame_id)
        if exame is None:
            raise LookupError('exame not found')

        return make_response(exame)

    @post(r"^/exames/$")
    @validate_body(ExameFieldsValidator)
    async def create_exame(self, request: Request):
        body = await request.get_body()
        exame: Exame = self.exame_repository.create(body['type'])
        return make_response(exame, 201)

    @patch(r"^/exames/(?P<id>\d+)/marcar$")
    @validate_params(IdValidator)
    async def marcar_exame(self, request: Request, id: str):
        exame_id = int(id)
        exame = self.exame_repository.update(exame_id, {'marcado': True})
        if exame is None:
            raise LookupError('exame not found')

        return make_response(exame)

    @put(r"^/exames/(?P<id>\d+)$")
    @validate_body(ExameFieldsValidator)
    @validate_params(IdValidator)
    async def update_exame(self, request: Request, id: str):
        exame_id = int(id)
        body = await request.get_body()
        exame: Optional[Exame] = self.exame_repository.update(exame_id, body)
        if not exame:
            raise LookupError("exame not found")

        return make_response(exame)

    @delete(r"^/exames/(?P<id>\d+)$")
    @validate_params(IdValidator)
    async def delete_exame(self, request: Request, id: str):
        exame_id = int(id)
        success: bool = self.exame_repository.delete(exame_id)
        if not success:
            raise LookupError("exame not found")

        return make_response({})
    

"""
class Exame(DomainModel):
    def __init__(
        self,
        id: int,
        tipo: str,
        data: date,
        marcado: bool,
        resultado: Optional[str] = None,
        laboratorio: Optional[str] = None,
        consulta_id: Optional[int] = None,
        paciente_id: Optional[int] = None
    ):
        self.id = id
        self.tipo = tipo
        self.data = data
        self.marcado = marcado
        self.resultado = resultado
        self.laboratorio = laboratorio
        self.consulta_id = consulta_id
        self.paciente_id = paciente_id
    """
