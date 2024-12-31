from ._base import BaseRouter
from src.controllers import TarefaController
from src.repository import TarefaRepository


class TarefaRouter(BaseRouter):
    def __init__(self, session):
        repository = TarefaRepository(session)
        controller = TarefaController(repository)

        self.register_endpoints((
            controller.get_tarefa,
            controller.create_tarefa,
            controller.update_tarefa,
            controller.delete_tarefa
        ))
