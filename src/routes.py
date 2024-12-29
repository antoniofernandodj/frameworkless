
from abc import ABC
from src.controllers.todo import TodosController
from src.controllers.user import UserController
from src.infra.database import SessionLocal
from src.repository import TodosRepository, UserRepository
import re


class BaseRouter(ABC):

    routes: dict

    def match_route(self, method, path):
        for pattern, methods in self.routes.items():
            compiled_pattern = re.compile(pattern)
            match = compiled_pattern.match(path)
            
            if match and method in methods:
                return methods[method], match.groupdict()

        return None, None





class UserRouter(BaseRouter):
    def __init__(self):
        self.session = SessionLocal()
        self.user_repository = UserRepository(self.session)
        self.todos_repository = TodosRepository(self.session)
        self.user_controller = UserController(self.user_repository)
        self.todo_controller = TodosController(self.todos_repository)

        self.routes = {
            r"^/user/$": {
                'GET': self.user_controller.get_user_handler,
                'POST': self.user_controller.create_user_handler
            },
            r"^/user/(?P<id>\d+)$": {
                'PUT': self.user_controller.update_user_handler,
                'DELETE': self.user_controller.delete_user_handler
            }
        }


class TodosRouter(BaseRouter):
    def __init__(self):
        self.session = SessionLocal()
        self.user_repository = UserRepository(self.session)
        self.todos_repository = TodosRepository(self.session)
        self.user_controller = UserController(self.user_repository)
        self.todo_controller = TodosController(self.todos_repository)

        self.routes = {
            r"^/todos/$": {
                'GET': self.todo_controller.get_todos_handler,
                'POST': self.todo_controller.create_todo_handler
            },
            r"^/todos/(?P<id>\d+)$": {
                'GET': self.todo_controller.get_todo_by_id_handler,
                'PUT': self.todo_controller.update_todo_handler,
                'DELETE': self.todo_controller.delete_todo_handler
            },
            r"^/todos/user/(?P<user_id>\d+)$": {
                'GET': self.todo_controller.get_todos_by_user_handler,
                'DELETE': self.todo_controller.delete_todos_by_user_handler
            }
        }
