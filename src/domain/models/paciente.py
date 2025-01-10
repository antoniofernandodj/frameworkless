from ._base import DomainModel
from datetime import date
from typing import Optional


class Paciente(DomainModel):
    def __init__(
        self,
        nome: str,
        login: str,
        password: str,
        data_nascimento: date,
        sexo: str,
        contato: Optional[str] = None,
        endereco: Optional[str] = None,
        responsavel: Optional[str] = None,
        _id: Optional[int] = None
    ):
        self._id = _id
        self.nome = nome
        self.login = login
        self.password = password
        self.data_nascimento = data_nascimento
        self.sexo = sexo
        self.contato = contato
        self.endereco = endereco
        self.responsavel = responsavel

    def to_response(self):
        paciente_dict = self.to_dict()
        paciente_dict.pop('password', None)
        return paciente_dict

