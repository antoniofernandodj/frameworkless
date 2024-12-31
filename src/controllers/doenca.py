from src.models import Request
from typing import Annotated, Optional
from src.domain.models import Doenca
from src.repository import DoencaRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, delete
)


class DoencaFieldsValidator(ParamsValidator):
    nome: Annotated[str, "Invalid doenca payload"]
    descricao: Annotated[str, "Invalid doenca payload"]
    cid: Annotated[str, "Invalid doenca payload"]
    paciente_id: Annotated[str, "Invalid doenca payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class DoencaController:
    def __init__(self, doenca_repository: DoencaRepository) -> None:
        self.doenca_repository = doenca_repository

    @get(r"^/doencas/$")
    @validate_params(IdValidator)
    async def get_doenca(self, request: Request):
        doenca_id: int = request.query['id']
        doenca: Optional[Doenca] = self.doenca_repository.get_by_id(doenca_id)
        if doenca is None:
            raise LookupError('doenca not found')

        return make_response(200, doenca.to_dict())

    @post(r"^/doencas/$")
    @validate_body(DoencaFieldsValidator)
    async def create_doenca(self, request: Request):
        body = await request.get_body()
        doenca: Doenca = self.doenca_repository.create(body['name'])
        return make_response(201, doenca.to_dict())

    @put(r"^/doencas/(?P<id>\d+)$")
    @validate_body(DoencaFieldsValidator)
    @validate_params(IdValidator)
    async def update_doenca(self, request: Request):
        doenca_id: int = request.path_args['id']
        body = await request.get_body()
        doenca: Optional[Doenca] = self.doenca_repository.update(doenca_id, body)
        if not doenca:
            raise LookupError("doenca not found")

        return make_response(200, doenca.to_dict())

    @delete(r"^/doencas/(?P<id>\d+)$")
    @validate_params(IdValidator)
    async def delete_doenca(self, request: Request):
        doenca_id: int = request.path_args['id']
        success: bool = self.doenca_repository.delete(doenca_id)
        if not success:
            raise LookupError("doenca not found")

        return make_response(200, {})


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