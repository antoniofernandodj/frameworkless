from ._base import BaseRouter
from src.controllers import ExameController
from src.repository import ExameRepository


class ExameRouter(BaseRouter):
    def __init__(self, session):
        repository = ExameRepository(session)
        controller = ExameController(repository)

        self.register_endpoints((
            controller.get_exame,
            controller.create_exame,
            controller.update_exame,
            controller.delete_exame,
            controller.marcar_exame
        ))
