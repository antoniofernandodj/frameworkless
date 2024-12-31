from ._base import DomainModel
from datetime import date
from typing import Optional


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
