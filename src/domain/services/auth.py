from asyncio import iscoroutinefunction
from datetime import date, datetime
from functools import wraps
from src.exceptions.http import ConflictError, NotFoundError, UnauthorizedError
from src.infra.database.sql import get_session_local
from src.jwt import JWTService
from typing import Any, Callable, Dict, Optional
from src.domain.models import Paciente
from src.models import Request
from src.repository import PacienteRepository
from src.security import HashService



class AuthService:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self.repo = paciente_repository

    def login(self, login: str, password: str) -> Dict[str, Any]:
        paciente = self.repo.get_by(login=login)
        if paciente is None:
            raise NotFoundError('Credenciais inválidas!')

        if not HashService.check_hash(password, paciente.password):
            raise UnauthorizedError('Credenciais inválidas!')

        token = JWTService.generate({'user_id': paciente.id})
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
            password=HashService.generate_hash(password)
        )

        result = self.repo.create(paciente)
        token = JWTService.generate({'user_id': result.id})
        response = result.to_response()
        response['token'] = token
        return response

    def get_user_by_token(self, token: str) -> Paciente:
        try:
            payload = JWTService.decode(token=token)
        except ValueError as e:
            raise UnauthorizedError(f'Erro ao decodificar o token: {e}')

        user_id = payload.get('user_id')
        expire_time_timestamp = payload.get('exp')

        if user_id is None or expire_time_timestamp is None:
            raise UnauthorizedError(f'Erro ao decodificar o token')

        if expire_time_timestamp is None or datetime.now().timestamp() > expire_time_timestamp:
            raise UnauthorizedError('O token expirou. Faça login novamente.')

        paciente = self.repo.get_by_id(user_id=user_id)
        if paciente is None:
            raise UnauthorizedError('Credenciais inválidas!')
        
        return paciente


def auth_required(func: Callable):

    @wraps(func)
    async def inner(self, request: Request):

        auth = (
            request.headers.get('Authorization') or 
            request.headers.get('authorization')
        )

        if auth is None:
            raise UnauthorizedError
        
        try:
            if 'bearer' in auth:
                _, token = auth.split('bearer ')
            elif 'Bearer' in auth:
                _, token = auth.split('Bearer ')
            else:
                raise Exception
        except:
            raise UnauthorizedError
        
        try:
            SessionLocal = get_session_local()
            with SessionLocal() as session:
                repo = PacienteRepository(session)
                service = AuthService(repo)
                current_user = service.get_user_by_token(token)
        except:
            raise UnauthorizedError

        if iscoroutinefunction(func):
            return await func(self, request, current_user)
        else:
            return func(self, request, current_user)
    
    return inner
    
