from ._base import DomainModel
from datetime import datetime
from typing import Optional


class Consulta(DomainModel):
    def __init__(
        self,
        horario: datetime,
        motivo: str,
        medico: str,
        especialidade: Optional[str] = None,
        local: Optional[str] = None,
        observacoes: Optional[str] = None,
        paciente_id: Optional[int] = None,
        doenca_id: Optional[int] = None,
        _id: Optional[int] = None,
        marcado: Optional[bool] = False
    ):
        self._id = _id
        self.horario = horario
        self.motivo = motivo
        self.medico = medico
        self.especialidade = especialidade
        self.local = local
        self.observacoes = observacoes
        self.paciente_id = paciente_id
        self.doenca_id = doenca_id
        self.marcado = marcado
