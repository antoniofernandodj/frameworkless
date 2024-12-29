
from abc import ABC
from src.controllers.todo import TodosController
from src.controllers.user import UserController
from src.infra.database import SessionLocal
from src.repository import TodosRepository, UserRepository
import re


class BaseRouter(ABC):

    routes: dict

    def match_route(self, method, path):
        if method not in self.routes:
            return None, None

        for pattern, handler in self.routes[method]:
            compiled_pattern = re.compile(pattern)
            match = compiled_pattern.match(path)
            if match:
                print({'path': path})
                return handler, match.groupdict()

        return None, None



class UserRouter(BaseRouter):
    def __init__(self):
        self.session = SessionLocal()
        self.user_repository = UserRepository(self.session)
        self.todos_repository = TodosRepository(self.session)
        self.user_controller = UserController(self.user_repository)
        self.todo_controller = TodosController(self.todos_repository)

        self.routes = {
            "GET": [
                (r"^/user/$", self.user_controller.get_user_handler),
            ],
            "POST": [
                (r"^/user/$", self.user_controller.create_user_handler),
            ],
            "PUT": [
                (r"^/user/(?P<id>\d+)$", self.user_controller.update_user_handler),
            ],
            "DELETE": [
                (r"^/user/(?P<id>\d+)$", self.user_controller.delete_user_handler),
            ],
        }


class TodosRouter(BaseRouter):
    def __init__(self):
        self.session = SessionLocal()
        self.user_repository = UserRepository(self.session)
        self.todos_repository = TodosRepository(self.session)
        self.user_controller = UserController(self.user_repository)
        self.todo_controller = TodosController(self.todos_repository)

        self.routes = {
            "GET": [
                (r"^/todos/$", self.todo_controller.get_todos_handler),
                (r"^/todos/(?P<id>\d+)$", self.todo_controller.get_todo_by_id_handler),
                (r"^/todos/user/(?P<user_id>\d+)$", self.todo_controller.get_todos_by_user_handler),
            ],
            "POST": [
                (r"^/todos/$", self.todo_controller.create_todo_handler),
            ],
            "PUT": [
                (r"^/todos/(?P<id>\d+)$", self.todo_controller.update_todo_handler),
            ],
            "DELETE": [
                (r"^/todos/(?P<id>\d+)$", self.todo_controller.delete_todo_handler),
                (r"^/todos/user/(?P<user_id>\d+)$", self.todo_controller.delete_todos_by_user_handler),
            ],
        }
