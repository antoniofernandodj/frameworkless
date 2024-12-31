from ._base import BaseRouter
from src.controllers import DoencaController
from src.repository import DoencaRepository


class DoencaRouter(BaseRouter):
    def __init__(self, session):
        repository = DoencaRepository(session)
        controller = DoencaController(repository)

        self.register_endpoints((
            controller.get_doenca,
            controller.create_doenca,
            controller.update_doenca,
            controller.delete_doenca
        ))
