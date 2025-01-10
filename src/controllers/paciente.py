from typing import Annotated, TypeVar

from src.exceptions.http import NotFoundError
from src.models import Request
from src.repository import PacienteRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, put, delete
)


class PacienteFieldsValidator(ParamsValidator):
    nome: Annotated[str, "Invalid paciente payload"]
    data_nascimento: Annotated[str, "Invalid paciente payload"]
    sexo: Annotated[str, "Invalid paciente payload"]
    contato: Annotated[str, "Invalid paciente payload"]
    endereco: Annotated[str, "Invalid paciente payload"]
    responsavel: Annotated[str, "Invalid paciente payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


T = TypeVar('T')


class PacienteController:

    url_prefix: str = '/pacientes/'

    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self.repo = paciente_repository

    @get("/")
    @validate_params(IdValidator)
    async def get_paciente(self, request: Request):
        id: int = request.query['id']
        paciente = self.repo.get_by_id(id)
        if paciente is None:
            raise NotFoundError('Paciente não encontrado')
        return make_response(paciente)

    @put("/<id:int>")
    @validate_params(IdValidator)
    async def update_paciente(self, request: Request, id: int):
        body = await request.get_body(PacienteFieldsValidator)
        paciente = self.repo.update(id, body)
        if paciente is None:
            raise NotFoundError('Paciente não encontrado')
        return make_response(paciente)

    @delete("/<id:int>")
    @validate_params(IdValidator)
    async def delete_paciente(self, request: Request, id: int):
        success = self.repo.delete(id)
        if not success:
            raise NotFoundError('Paciente não encontrado')
        return make_response(204)
