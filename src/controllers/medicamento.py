from typing import Annotated, Optional
from datetime import date

from src.exceptions.http import NotFoundError
from src.models import Request
from src.domain.models import Medicamento
from src.repository import MedicamentoRepository
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, post, put, delete
)


class MedicamentoFieldsValidator(ParamsValidator):
    nome: Annotated[str, "`nome` required"]
    dosagem: Annotated[str, "`dosagem` required"]
    frequencia: Annotated[str, "`` required"]
    # via: Annotated[str, "`` required"]
    inicio_tratamento: Annotated[date, "`inicio_tratamento` must be a valid ISO date"]
    # fim_tratamento: Annotated[Optional[date], "`fim_tratamento` must be a valid ISO date"]
    paciente_id: Annotated[int, "`paciente_id` required"]
    # doenca_id: Annotated[int, "`doenca_id` required"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class MedicamentoController:

    url_prefix: str = '/medicamentos/'

    def __init__(self, medicamento_repository: MedicamentoRepository) -> None:
        self.medicamento_repository = medicamento_repository

    @get("/")
    @validate_params(IdValidator)
    async def get_medicamento(self, request: Request):
        medicamento_id: int = request.query['id']
        medicamento: Optional[Medicamento] = self.medicamento_repository.get_by_id(medicamento_id)
        if medicamento is None:
            raise NotFoundError('medicamento not found')
        return make_response(medicamento)

    @post("/")
    async def create_medicamento(self, request: Request):
        body = await request.get_body(MedicamentoFieldsValidator)
        # body.inicio_tratamento = date.fromisoformat(body.pop('inicio_tratamento'))
        # if body.get('fim_tratamento'):
        #     body.fim_tratamento = date.fromisoformat(body.pop('fim_tratamento'))
        m = Medicamento(**body)
        medicamento: Medicamento = self.medicamento_repository.create(m)
        return make_response(medicamento, 201)

    @put("/<id:int>")
    async def update_medicamento(self, request: Request, id: str):
        medicamento_id = int(id)
        body = await request.get_body(MedicamentoFieldsValidator)
        # body.inicio_tratamento = date.fromisoformat(body.pop('inicio_tratamento'))
        # if body.get('fim_tratamento'):
        #     body.fim_tratamento = date.fromisoformat(body.pop('fim_tratamento'))
        medicamento: Optional[Medicamento] = self.medicamento_repository.update(medicamento_id, body)
        if not medicamento:
            raise NotFoundError("medicamento not found")
        return make_response(medicamento)

    @delete("/<id:int>")
    async def delete_medicamento(self, request: Request, id: str):
        medicamento_id = int(id)
        success: bool = self.medicamento_repository.delete(medicamento_id)
        if not success:
            raise NotFoundError("medicamento not found")
        return make_response(204)
