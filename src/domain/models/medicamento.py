from ._base import DomainModel
from datetime import date
from typing import Optional


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
