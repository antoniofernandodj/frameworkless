from typing import Any

from src.controllers.auth import AuthService
from ._base import BaseRouter
from src.controllers import AuthController
from src.repository import PacienteRepository

class AuthRouter(BaseRouter):
    def __init__(self, session: Any):
        repository = PacienteRepository(session)
        service = AuthService(repository)
        controller = AuthController(service)
        self.register_controller(controller)
