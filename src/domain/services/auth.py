from datetime import date
from src.exceptions.http import ConflictError, NotFoundError
from src.jwt import generate_jwt
from typing import Any, Dict, Optional
from src.domain.models import Paciente
from src.repository import PacienteRepository
from src.security import HashService



class AuthService:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self.repo = paciente_repository

    def login(self, login: str, password: str) -> Dict[str, Any]:
        paciente = self.repo.get_by(login=login)
        if paciente is None or not HashService.check_hash(password, paciente.senha):
            raise NotFoundError('Credenciais inválidas!')

        token = generate_jwt({'user_id': paciente.id})
        response = paciente.to_response()
        response['token'] = token
        return response

    def signin(
        self,
        nome: str,
        login: str,
        password: str,
        data_nascimento: str,
        sexo: str,
        contato: Optional[str] = None,
        endereco: Optional[str] = None,
        responsavel: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.repo.get_by(login=login) is not None:
            raise ConflictError('Login já existe!')

        data_nascimento_str = date.fromisoformat(data_nascimento)
        paciente = Paciente(
            nome=nome,
            data_nascimento=data_nascimento_str,
            sexo=sexo,
            contato=contato,
            endereco=endereco,
            responsavel=responsavel,
            login=login,
            senha=HashService.generate_hash(password)
        )

        result = self.repo.create(paciente)
        token = generate_jwt({'user_id': result.id})
        response = result.to_response()
        response['token'] = token
        return response
