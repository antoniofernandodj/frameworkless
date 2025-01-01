from ._base import BaseRouter
from src.controllers import MedicamentoController
from src.repository import MedicamentoRepository


class MedicamentoRouter(BaseRouter):
    def __init__(self, session):
        repository = MedicamentoRepository(session)
        controller = MedicamentoController(repository)
        self.register_controller(controller)