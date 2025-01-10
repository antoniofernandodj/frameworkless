from src.exceptions.http import NotFoundError, UnprocessableEntityError
from src.models import Request
from typing import Annotated, Optional
from src.domain.models import Doenca
from src.repository import DoencaRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, post, put, delete
)


class DoencaFieldsValidator(ParamsValidator):
    nome: Annotated[str, "`nome` required"]
    descricao: Annotated[str, "`descricao` required"]
    codigo_cid: Annotated[str, "`codigo_cid` required"]
    paciente_id: Annotated[str, "`paciente_id` required"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "`id` is required"]


class DoencaController:

    url_prefix: str = '/doencas/'

    def __init__(self, doenca_repository: DoencaRepository) -> None:
        self.doenca_repository = doenca_repository

    @get("/")
    @validate_params(IdValidator)
    async def get_doenca(self, request: Request):
        doenca_id: int = request.query['id']
        doenca: Optional[Doenca] = self.doenca_repository.get_by_id(doenca_id)
        if doenca is None:
            raise NotFoundError('Doença not found')
        return make_response(doenca)

    @post("/")
    async def create_doenca(self, request: Request):
        body = await request.get_body(DoencaFieldsValidator)
        doenca = Doenca(**body)
        doenca: Doenca = self.doenca_repository.create(doenca)
        return make_response(doenca, 201)

    @put("/<id:int>")
    async def update_doenca(self, request: Request, id: str):
        doenca_id = int(id)
        body = await request.get_body(DoencaFieldsValidator)
        doenca: Optional[Doenca] = self.doenca_repository.update(doenca_id, body)
        if not doenca:
            raise NotFoundError('Doença not found')
        return make_response(doenca)

    @delete("/<id:int>")
    async def delete_doenca(self, request: Request, id: str):
        doenca_id = int(id)
        success: bool = self.doenca_repository.delete(doenca_id)
        if not success:
            raise NotFoundError('Doença not found')
        return make_response(204)


"""

class Doenca(DomainModel):
    def __init__(
        self,
        id: int,
        nome: str,
        descricao: Optional[str] = None,
        codigo_cid: Optional[str] = None,
        paciente_id: Optional[int] = None
    ):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.codigo_cid = codigo_cid
        self.paciente_id = paciente_id



"""