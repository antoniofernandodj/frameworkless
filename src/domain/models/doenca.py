from ._base import DomainModel
from typing import Optional


class Doenca(DomainModel):
    def __init__(
        self,
        nome: str,
        descricao: Optional[str] = None,
        codigo_cid: Optional[str] = None,
        paciente_id: Optional[int] = None,
        _id: Optional[int] = None
    ):
        self._id = _id
        self.nome = nome
        self.descricao = descricao
        self.codigo_cid = codigo_cid
        self.paciente_id = paciente_id

