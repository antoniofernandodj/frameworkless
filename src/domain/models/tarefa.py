from ._base import DomainModel
from datetime import date
from typing import Optional


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