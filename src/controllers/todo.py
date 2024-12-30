from typing import Annotated, Any, Dict, List
from src.domain.models import Todo
from src.exceptions.http import NotFoundError
from src.repository import TodosRepository
from src.utils import ParamsValidator, make_response, validate_body, validate_params
from typing import Dict, Any


class TodoIdValidator(ParamsValidator):
    id: Annotated[int, "Id is required!"]


class UserIdParamValidator(ParamsValidator):
    user_id: Annotated[int, "User id is required!"]


class UpdateTodoBodyValidator(ParamsValidator):
    task: Annotated[str, "Invalid task payload"]


class CreateTodoBodyValidator(ParamsValidator):
    task: Annotated[str, "Task is required in payload"]
    user: Annotated[int, "User id is required in payload"]



class TodosController:
    def __init__(self, todos_repository: TodosRepository) -> None:
        self.todos_repository = todos_repository

    async def get_todos_handler(self, params: Dict[str, Any], _):
        todos: List[Todo] = self.todos_repository.get_todos(params)
        body = {"todos": [todo.dict() for todo in todos]}
        return make_response(200, body)

    @validate_params(UserIdParamValidator)
    async def get_todos_by_user_handler(self, params: Dict[str, Any], _):
        user_id: int = params['user_id']
        todos: List[Todo] = self.todos_repository.get_todos_by_user(user_id)
        body = {"todos": [todo.dict() for todo in todos]}
        return make_response(200, body)

    @validate_params(TodoIdValidator)
    async def get_todo_by_id_handler(self, params: Dict[str, Any], _):
        todo_id: int = params['id']
        todo = self.todos_repository.get_by_id(todo_id)
        if todo is None:
            raise NotFoundError("Todo not found")

        body = todo.dict()
        return make_response(200, body)

    @validate_body(CreateTodoBodyValidator)
    async def create_todo_handler(self, _, request_body):
        todo: Todo = self.todos_repository.create_todo(
            request_body["task"], request_body["user"]
        )

        body = todo.dict()
        return make_response(201, body)

    @validate_body(UpdateTodoBodyValidator)
    @validate_params(TodoIdValidator)
    async def update_todo_handler(self, params: Dict[str, Any], request_body):
        todo_id: int = params["id"]
        task: str = request_body["task"]

        todo = self.todos_repository.update_todo(todo_id, task)
        if not todo:
            raise NotFoundError("Todo not found")

        body = todo.dict()
        return make_response(200, body)

    @validate_params(TodoIdValidator)
    async def delete_todo_handler(self, params: Dict[str, Any], _):
        todo_id: int = params['id']
        success: bool = self.todos_repository.delete_todo(todo_id)
        if not success:
            raise NotFoundError("Todo not found")

        body = {}
        return make_response(200, body)

    @validate_params(UserIdParamValidator)
    async def delete_todos_by_user_handler(self, params: Dict[str, Any], _):
        user_id: int = params["user_id"]
        count: int = self.todos_repository.delete_todos_by_user(user_id)
        if count == 0:
            raise NotFoundError("No todos found for user")

        body = {"deleted_count": count}
        return make_response(200, body)
