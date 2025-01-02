from datetime import date
from src.exceptions.http import ConflictError, NotFoundError, UnauthorizedError, UnprocessableEntityError
from src.jwt import generate_jwt
from src.models import Request
from typing import Annotated, Any, Dict, Generic, Optional, TypeVar
from src.domain.models import Paciente
from src.repository import PacienteRepository, GenericRepository
from src.security import HashService
from src.utils import (
    ParamsValidator,
    make_response,
    validate_body,
    validate_params,
    get, post, put, delete
)


T = TypeVar('T')


class SignInValidator(ParamsValidator):
    nome: Annotated[str, 'Nome requeridi']
    login: Annotated[str, 'Login requerido']
    password: Annotated[str, 'Password requerido']
    data_nascimento: Annotated[str, 'Data de nascimento requerido']
    sexo: Annotated[str, 'Sexo requerido']
    # contato: Annotated[str, '']
    # endereco: Annotated[str, '']
    # responsavel: Annotated[str, '']

class LoginInValidator(ParamsValidator):
    login: Annotated[str, 'Login requerido']
    password: Annotated[str, 'Password requerido']








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




class AuthController:

    def __init__(self, auth_service: AuthService) -> None:
        self.service = auth_service

    @post("/login/")
    async def login(self, request: Request):
        body = await request.get_body(LoginInValidator)
        if body is None:
            raise UnprocessableEntityError('Body vazio')

        response = self.service.login(login=body.login, password=body.password)
        return make_response(response)

    @post("/signin/")
    async def signin(self, request: Request):
        body = await request.get_body(SignInValidator)
        if body is None:
            raise UnprocessableEntityError('Body vazio')

        response = self.service.signin(
            nome=body.nome,
            login=body.login,
            password=body.password,
            data_nascimento=body.data_nascimento,
            sexo=body.sexo,
            contato=getattr(body, 'contato', None),
            endereco=getattr(body, 'endereco', None),
            responsavel=getattr(body, 'responsavel', None),
        )
        return make_response(response, 201)
