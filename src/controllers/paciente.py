from src.exceptions.http import NotFoundError, UnprocessableEntityError
from src.models import Request
from typing import Annotated, Any, Dict, Generic, Optional, TypeVar
from src.domain.models import Paciente
from src.repository import PacienteRepository, GenericRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, delete
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

    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self.repo = paciente_repository

    @get("/pacientes/")
    @validate_params(IdValidator)
    async def get_paciente(self, request: Request):
        id: int = request.query['id']
        paciente = self.repo.get_by_id(id)
        if paciente is None:
            raise NotFoundError('Paciente não encontrado')
        return make_response(paciente)

    @put("/pacientes/<id:int>")
    @validate_body(PacienteFieldsValidator)
    @validate_params(IdValidator)
    async def update_paciente(self, request: Request, id: int):
        body = await request.get_body(None)
        if body is None:
            raise UnprocessableEntityError
        paciente = self.repo.update(id, body)
        if paciente is None:
            raise NotFoundError('Paciente não encontrado')
        return make_response(paciente)

    @delete("/pacientes/<id:int>")
    @validate_params(IdValidator)
    async def delete_paciente(self, request: Request, id: int):
        success = self.repo.delete(id)
        if not success:
            raise NotFoundError('Paciente não encontrado')
        return make_response(204)




"""

class Paciente(DomainModel):
    def __init__(
        self,
        id: int,
        nome: str,
        data_nascimento: date,
        sexo: str,
        contato: Optional[str] = None,
        endereco: Optional[str] = None,
        responsavel: Optional[str] = None
    ):
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.sexo = sexo
        self.contato = contato
        self.endereco = endereco
        self.responsavel = responsavel

"""