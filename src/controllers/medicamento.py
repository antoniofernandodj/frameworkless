from src.exceptions.http import NotFoundError, UnprocessableEntityError
from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Medicamento
from src.repository import MedicamentoRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, delete
)


class MedicamentoFieldsValidator(ParamsValidator):
    nome: Annotated[str, "Invalid medicamento payload"]
    dosagem: Annotated[str, "Invalid medicamento payload"]
    frequencia: Annotated[str, "Invalid medicamento payload"]
    via: Annotated[str, "Invalid medicamento payload"]
    inicio_tratamento: Annotated[str, "Invalid medicamento payload"]
    fim_tratamento: Annotated[str, "Invalid medicamento payload"]
    paciente_id: Annotated[int, "Invalid medicamento payload"]
    doenca_id: Annotated[int, "Invalid medicamento payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class MedicamentoController:
    def __init__(self, medicamento_repository: MedicamentoRepository) -> None:
        self.medicamento_repository = medicamento_repository

    @get("/medicamentos/")
    @validate_params(IdValidator)
    async def get_medicamento(self, request: Request):
        medicamento_id: int = request.query['id']
        medicamento: Optional[Medicamento] = self.medicamento_repository.get_by_id(medicamento_id)
        if medicamento is None:
            raise NotFoundError('medicamento not found')
        return make_response(medicamento)

    @post("/medicamentos/")
    @validate_body(MedicamentoFieldsValidator)
    async def create_medicamento(self, request: Request):
        body = await request.get_body()
        medicamento: Medicamento = self.medicamento_repository.create(body['name'])
        return make_response(medicamento, 201)

    @put("/medicamentos/<id:int>")
    @validate_body(MedicamentoFieldsValidator)
    @validate_params(IdValidator)
    async def update_medicamento(self, request: Request, id: str):
        medicamento_id = int(id)
        body = await request.get_body()
        medicamento: Optional[Medicamento] = self.medicamento_repository.update(medicamento_id, body)
        if not medicamento:
            raise NotFoundError("medicamento not found")
        return make_response(medicamento)

    @delete("/medicamentos/<id:int>")
    @validate_params(IdValidator)
    async def delete_medicamento(self, request: Request, id: str):
        medicamento_id = int(id)
        success: bool = self.medicamento_repository.delete(medicamento_id)
        if not success:
            raise NotFoundError("medicamento not found")
        return make_response(204)


"""
class Medicamento(DomainModel):

    def __init__(
        self,
        id: int,
        nome: str,
        dosagem: str,
        frequencia: str,
        via: Optional[str] = None,
        inicio_tratamento: Optional[date] = None,
        fim_tratamento: Optional[date] = None,
        paciente_id: Optional[int] = None,
        doenca_id: Optional[int] = None
    ):
        self.id = id
        self.nome = nome
        self.dosagem = dosagem
        self.frequencia = frequencia
        self.via = via
        self.inicio_tratamento = inicio_tratamento
        self.fim_tratamento = fim_tratamento
        self.paciente_id = paciente_id
        self.doenca_id = doenca_id


"""