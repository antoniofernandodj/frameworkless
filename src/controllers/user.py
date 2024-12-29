from typing import Any, Dict
from src.exceptions.http import NotFoundError
from src.repository import UserRepository
from src.utils import ParamsValidator, make_response, validate_body, validate_params
from typing import Dict, Any


user_id_validator = (
    ParamsValidator()
    .add(
        param_name="id",
        param_type=int,
        msg="Id is required"
    )
)


user_name_validator = (
    ParamsValidator()
    .add(
        param_name="name",
        param_type=str,
        msg="Invalid user payload"
    )
)


class UserController:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    @validate_params(user_id_validator)
    async def get_user_handler(self, params: Dict[str, Any], _):
        user_id = params['id']
        print({'id': user_id})
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError('User not found')

        body = user.dict()
        return make_response(200, body)

    @validate_body(user_name_validator)
    async def create_user_handler(self, params: Dict[str, Any], body):
        user = self.user_repository.create_user(body['name'])
        body = user.dict()
        return make_response(201, body)

    @validate_body(user_name_validator)
    @validate_params(user_id_validator)
    async def update_user_handler(self, params: Dict[str, Any], body):
        user_id = params['id']
        user = self.user_repository.update_user(user_id, body['name'])
        if not user:
            raise NotFoundError("User not found")

        body = user.dict()
        return make_response(200, body)
    
    @validate_params(user_id_validator)
    async def delete_user_handler(self, params: Dict[str, Any], _):
        user_id = params['id']
        success = self.user_repository.delete_user(user_id)
        if not success:
            raise NotFoundError("User not found")

        body = {}
        return make_response(200, body)

