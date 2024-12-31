from ._base import BaseRouter
from src.controllers.paciente import PacienteController
from src.repository import PacienteRepository


class PacienteRouter(BaseRouter):
    def __init__(self, session):
        repository = PacienteRepository(session)
        controller = PacienteController(repository)

        self.register_endpoints((
            controller.get_paciente,
            controller.create_paciente,
            controller.update_paciente,
            controller.delete_paciente
        ))
