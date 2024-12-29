from typing import Any, Dict
from src.exceptions.http import NotFoundError
from src.repository import TodosRepository
from src.utils import ParamsValidator, make_response, validate_body, validate_params
from typing import Dict, Any


user_id_validator = (
    ParamsValidator()
    .add(
        param_name="user_id",
        param_type=int,
        msg="User id is required"
    )
)


todo_id_validator = (
    ParamsValidator()
    .add(
        param_name="id",
        param_type=int,
        msg="Id is required"
    )
)


# class TodoIdValidator(ParamsValidator):
#     id: Annotated[int, 'Id is required!']


create_todo_body_validator = (
    ParamsValidator()
    .add(
        param_name="task",
        param_type=str,
        msg="Invalid task payload"
    )
    .add(
        param_name="user",
        param_type=int,
        msg="Invalid task payload"
    )
)


update_todo_body_validator = (
    ParamsValidator()
    .add(
        param_name="task",
        param_type=str,
        msg="Invalid task payload"
    )
)


class TodosController:
    def __init__(self, todos_repository: TodosRepository) -> None:
        self.todos_repository = todos_repository

    async def get_todos_handler(self, params: Dict[str, Any], receive):
        todos = self.todos_repository.get_todos(params)
        body = {"todos": [todo.dict() for todo in todos]}
        return make_response(200, body)

    @validate_params(user_id_validator)
    async def get_todos_by_user_handler(self, params: Dict[str, Any], _):
        user_id = params['user_id']
        todos = self.todos_repository.get_todos_by_user(user_id)
        body = {"todos": [todo.dict() for todo in todos]}
        return make_response(200, body)

    @validate_params(todo_id_validator)
    async def get_todo_by_id_handler(self, params: Dict[str, Any], _):
        todo_id = params['id']
        todo = self.todos_repository.get_by_id(todo_id)
        if todo is None:
            raise NotFoundError("Todo not found")

        body = todo.dict()
        return make_response(200, body)

    @validate_body(create_todo_body_validator)
    async def create_todo_handler(self, _, body):
        todo = self.todos_repository.create_todo(body["task"], body["user"])

        body = todo.dict()
        return make_response(201, body)

    @validate_body(update_todo_body_validator)
    @validate_params(todo_id_validator)
    async def update_todo_handler(self, params: Dict[str, Any], body):
        todo_id = params["id"]
        task = body["task"]

        todo = self.todos_repository.update_todo(todo_id, task)
        if not todo:
            raise NotFoundError("Todo not found")

        body = todo.dict()
        return make_response(200, body)

    @validate_params(todo_id_validator)
    async def delete_todo_handler(self, params: Dict[str, Any], _):
        todo_id = params['id']
        success = self.todos_repository.delete_todo(todo_id)
        if not success:
            raise NotFoundError("Todo not found")

        body = {}
        return make_response(200, body)

    @validate_params(user_id_validator)
    async def delete_todos_by_user_handler(self, params: Dict[str, Any], _):
        user_id = params["user_id"]
        count = self.todos_repository.delete_todos_by_user(user_id)
        if count == 0:
            raise NotFoundError("No todos found for user")

        body = {"deleted_count": count}
        return make_response(200, body)
