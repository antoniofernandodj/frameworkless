from src.exceptions.http import NotFoundError
from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Paciente
from src.repository import PacienteRepository
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


class PacienteController:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self.paciente_repository = paciente_repository

    @get(r"^/pacientes/$")
    @validate_params(IdValidator)
    async def get_paciente(self, request: Request):
        paciente_id: int = request.query['id']
        paciente: Optional[Paciente] = self.paciente_repository.get_by_id(paciente_id)
        if paciente is None:
            raise NotFoundError('paciente not found')

        return make_response(paciente)

    @post(r"^/pacientes/$")
    @validate_body(PacienteFieldsValidator)
    async def create_paciente(self, request: Request):
        body = await request.get_body()
        paciente: Paciente = self.paciente_repository.create(body['name'])
        return make_response(paciente, 201)

    @put(r"^/pacientes/(?P<id>\d+)$")
    @validate_body(PacienteFieldsValidator)
    @validate_params(IdValidator)
    async def update_paciente(self, request: Request, id: str):
        paciente_id = int(id)
        body = await request.get_body()
        paciente: Optional[Paciente] = self.paciente_repository.update(paciente_id, body['name'])
        if paciente is None:
            raise NotFoundError("paciente not found")

        return make_response(paciente)

    @delete(r"^/pacientes/(?P<id>\d+)$")
    @validate_params(IdValidator)
    async def delete_paciente(self, request: Request, id: str):
        paciente_id = int(id)
        success: bool = self.paciente_repository.delete(paciente_id)
        if not success:
            raise NotFoundError("paciente not found")

        return make_response({})


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