from src.domain.services.consulta import ConsultaService
from ._base import BaseRouter
from src.controllers import ConsultaController
from src.repository import ConsultaRepository

class ConsultaRouter(BaseRouter):
    def __init__(self, session):
        repository = ConsultaRepository(session)
        controller = ConsultaController(repository)

        self.register_endpoints((
            controller.get_consulta,
            controller.create_consulta,
            controller.update_consulta,
            controller.delete_consulta
        ))
