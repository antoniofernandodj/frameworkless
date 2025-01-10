from datetime import date
from src.domain.services.auth import AuthService, auth_required
from src.exceptions.http import ConflictError, NotFoundError, UnauthorizedError, UnprocessableEntityError
from src.jwt import JWTService
from src.models import Request
from typing import Annotated, Any, Dict, Generic, Optional, TypeVar
from src.domain.models import Paciente
from src.repository import PacienteRepository, GenericRepository
from src.security import HashService
from src.utils import (
    ParamsValidator,
    make_response,
    validate_params,
    get, post, put, delete
)


T = TypeVar('T')


class SignInValidator(ParamsValidator):
    nome: Annotated[str, 'Nome requerido']
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



class AuthController:

    url_prefix: str = '/auth/'

    def __init__(self, auth_service: AuthService) -> None:
        self.service = auth_service

    @post("/login/")
    async def login(self, request: Request):
        body = await request.get_body(validator=LoginInValidator)
        response = self.service.login(login=body.login, password=body.password)
        return make_response(response)

    @post("/signin/")
    async def signin(self, request: Request):
        body = await request.get_body(validator=SignInValidator)
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

    @post("/data")
    @auth_required
    async def auth_test(self, request: Request, current_user: Paciente):
        return make_response(current_user.to_response(), 200)
