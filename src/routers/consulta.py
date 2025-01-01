from typing import Any
from ._base import BaseRouter
from src.controllers import ConsultaController
from src.repository import ConsultaRepository

class ConsultaRouter(BaseRouter):
    def __init__(self, session: Any):
        repository = ConsultaRepository(session)
        controller = ConsultaController(repository)
        self.register_controller(controller)
