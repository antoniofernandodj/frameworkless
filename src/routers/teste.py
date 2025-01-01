from ._base import BaseRouter
from src.controllers import TesteController


class TesteRouter(BaseRouter):
    def __init__(self):
        controller = TesteController()
        self.register_controller(controller)
