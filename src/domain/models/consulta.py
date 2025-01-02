from ._base import DomainModel
from datetime import date
from typing import Optional


class Consulta(DomainModel):
    def __init__(
        self,
        data: date,
        marcado: bool,
        medico: str,
        especialidade: Optional[str] = None,
        local: Optional[str] = None,
        observacoes: Optional[str] = None,
        paciente_id: Optional[int] = None,
        doenca_id: Optional[int] = None,
        _id: Optional[int] = None
    ):
        self._id = _id
        self.data = data
        self.marcado = marcado
        self.medico = medico
        self.especialidade = especialidade
        self.local = local
        self.observacoes = observacoes
        self.paciente_id = paciente_id
        self.doenca_id = doenca_id
