from typing import Annotated, Optional
from datetime import date

from src.exceptions.http import NotFoundError
from src.models import Request
from src.domain.models import Exame
from src.repository import ExameRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, post, put, patch, delete
)


class ExameFieldsValidator(ParamsValidator):
    tipo: Annotated[str, "`tipo` required"]
    data: Annotated[str, "`data` required"]
    laboratorio: Annotated[str, "`laboratorio` required"]
    # consulta: Annotated[str, "`consulta` required"]
    paciente_id: Annotated[str, "`paciente_id` required"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class ExameController:

    url_prefix: str = '/exames/'

    def __init__(self, exame_repository: ExameRepository) -> None:
        self.exame_repository = exame_repository

    @get("/")
    @validate_params(IdValidator)
    async def get_exame(self, request: Request):
        exame_id: int = request.query['id']
        exame: Optional[Exame] = self.exame_repository.get_by_id(exame_id)
        if exame is None:
            raise NotFoundError('Exame not found')
        return make_response(exame)

    @post("/")
    async def create_exame(self, request: Request):
        body = await request.get_body(ExameFieldsValidator)
        body.data = date.fromisoformat(body.pop('data'))
        exame = Exame(**body)
        exame: Exame = self.exame_repository.create(exame)
        return make_response(exame, 201)

    @patch("/<id:int>/marcar")
    async def marcar_exame(self, request: Request, id: str):
        exame_id = int(id)
        body = await request.get_body()
        marcado = (getattr(body, 'marcar', None) or True) if body else True
        exame = self.exame_repository.update(exame_id, {
            'marcado': marcado
        })
        if exame is None:
            raise NotFoundError('Exame not found')
        return make_response(exame)

    @put("/<id:int>")
    async def update_exame(self, request: Request, id: str):
        exame_id = int(id)
        body = await request.get_body(ExameFieldsValidator)
        exame: Optional[Exame] = self.exame_repository.update(exame_id, body)
        if not exame:
            raise NotFoundError("Exame not found")
        return make_response(exame)

    @delete("/<id:int>")
    async def delete_exame(self, request: Request, id: str):
        exame_id = int(id)
        success: bool = self.exame_repository.delete(exame_id)
        if not success:
            raise NotFoundError("Exame not found")
        return make_response(204)
