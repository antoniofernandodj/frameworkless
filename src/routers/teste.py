from ._base import BaseRouter
from src.controllers import TesteController


class TesteRouter(BaseRouter):
    def __init__(self):
        controller = TesteController()

        self.register_endpoints((
            controller.teste_endpoint_1,
            controller.teste_endpoint_2,
            controller.teste_endpoint_3,
            controller.teste_endpoint_4,
            controller.teste_endpoint_5,
        ))
