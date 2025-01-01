from src.models import Request
from typing import Annotated, Any, Dict, Optional
from src.domain.models import Tarefa
from src.repository import TarefaRepository
from src.exceptions.http import NotFoundError
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, patch, delete
)


class TarefaFieldsValidator(ParamsValidator):
    descricao: Annotated[str, "Invalid tarefa payload"]
    data_limite: Annotated[str, "Invalid tarefa payload"]
    status: Annotated[str, "Invalid tarefa payload"]
    paciente_id: Annotated[int, "Invalid tarefa payload"]


class IdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class TarefaController:
    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self.tarefa_repository = tarefa_repository

    @get(r"^/tarefas/$")
    @validate_params(IdValidator)
    async def get_tarefa(self, request: Request):
        tarefa_id: int = request.query['id']
        tarefa: Optional[Tarefa] = self.tarefa_repository.get_by_id(tarefa_id)
        if tarefa is None:
            raise NotFoundError('tarefa not found')

        return make_response(tarefa)

    @post(r"^/tarefas/$")
    @validate_body(TarefaFieldsValidator)
    async def create_tarefa(self, request: Request):
        body = await request.get_body()
        tarefa: Tarefa = self.tarefa_repository.create(body['description'])
        return make_response(tarefa, 201)

    @put(r"^/tarefas/(?P<id>\d+)$")
    @validate_body(TarefaFieldsValidator)
    @validate_params(IdValidator)
    async def update_tarefa(self, request: Request, id: str):
        tarefa_id = int(id)
        body = await request.get_body()
        tarefa: Optional[Tarefa] = self.tarefa_repository.update(tarefa_id, body)
        if not tarefa:
            raise NotFoundError("tarefa not found")

        return make_response(tarefa)

    @delete(r"^/tarefas/(?P<id>\d+)$")
    @validate_params(IdValidator)
    async def delete_tarefa(self, request: Request, id: str):
        paciente_id = int(id)
        success: bool = self.tarefa_repository.delete(paciente_id)
        if not success:
            raise NotFoundError("Tarea not found")

        return make_response({})


"""


class Tarefa(DomainModel):
    def __init__(
        self,
        id: int,
        descricao: str,
        data_limite: Optional[date] = None,
        status: Optional[str] = None,
        paciente_id: Optional[int] = None
    ):
        self.id = id
        self.descricao = descricao
        self.data_limite = data_limite
        self.status = status
        self.paciente_id = paciente_id

"""