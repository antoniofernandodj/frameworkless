from ._base import DomainModel
from datetime import date
from typing import Optional


class Exame(DomainModel):
    def __init__(
        self,
        id: int,
        tipo: str,
        data: date,
        marcado: bool,
        resultado: Optional[str] = None,
        laboratorio: Optional[str] = None,
        consulta_id: Optional[int] = None,
        paciente_id: Optional[int] = None
    ):
        self.id = id
        self.tipo = tipo
        self.data = data
        self.marcado = marcado
        self.resultado = resultado
        self.laboratorio = laboratorio
        self.consulta_id = consulta_id
        self.paciente_id = paciente_id