from typing import Annotated, Any, Dict, Optional
from src.domain.models import User
from src.exceptions.http import NotFoundError
from src.repository import UserRepository
from src.utils import ParamsValidator, make_response, validate_body, validate_params
from typing import Dict, Any


class UserNameValidator(ParamsValidator):
    name: Annotated[str, "Invalid user payload"]


class UserIdValidator(ParamsValidator):
    id: Annotated[int, "Id is required"]


class UserController:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    @validate_params(UserIdValidator)
    async def get_user_handler(self, params: Dict[str, Any], _):
        user_id: int = params['id']
        user: Optional[User] = self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError('User not found')

        body = user.dict()
        return make_response(200, body)

    @validate_body(UserNameValidator)
    async def create_user_handler(self, params: Dict[str, Any], body):
        user: User = self.user_repository.create_user(body['name'])
        body = user.dict()
        return make_response(201, body)

    @validate_body(UserNameValidator)
    @validate_params(UserIdValidator)
    async def update_user_handler(self, params: Dict[str, Any], body):
        user_id: int = params['id']
        user: Optional[User] = self.user_repository.update_user(user_id, body['name'])
        if not user:
            raise NotFoundError("User not found")

        body = user.dict()
        return make_response(200, body)
    
    @validate_params(UserIdValidator)
    async def delete_user_handler(self, params: Dict[str, Any], _):
        user_id: int = params['id']
        success: bool = self.user_repository.delete_user(user_id)
        if not success:
            raise NotFoundError("User not found")

        body = {}
        return make_response(200, body)

