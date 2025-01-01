from ._base import BaseRouter
from src.controllers import ExameController
from src.repository import ExameRepository


class ExameRouter(BaseRouter):
    def __init__(self, session):
        repository = ExameRepository(session)
        controller = ExameController(repository)
        self.register_controller(controller)
