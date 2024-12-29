from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Type, get_type_hints, get_args, Annotated
import json
from functools import wraps
from typing import Callable, Coroutine, Dict, Any, List, Type, Union
from urllib.parse import parse_qs
from src.exceptions.http import UnprocessableEntityError


async def parse_body(receive) -> Union[List[Any], Dict[str, Any]]:
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

    return json.loads(body.decode("utf-8") or "{}")


def make_response(status: int, body):
    return {
        "status": status,
        "body": body
    }


def validate_params(params_validator: Type[ParamsValidator]) -> Callable:

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        async def wrapper(
            self,
            params: Dict[str, Any],
            body: Union[List[Any], Dict[str, Any], Coroutine]
        ) -> Dict[str, Any]:

            params = params_validator.validate(params)
            return await func(self, params, body)

        return wrapper
    return decorator


def validate_body(params_validator: Type[ParamsValidator]) -> Callable:

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        async def wrapper(
            self,
            params: Dict[str, Any],
            body: Union[List[Any], Dict[str, Any], Coroutine]
        ) -> Dict[str, Any]:

            if not isinstance(body, (dict, list)):
                body = await parse_body(body)

            if not isinstance(body, dict):
                raise UnprocessableEntityError('Must be a dict')

            body = params_validator.validate(body)
            return await func(self, params, body)

        return wrapper
    return decorator


def parse_request_body(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, params: Dict[str, Any], receive, *args, **kwargs):
        body = await parse_body(receive)
        return await func(self, params, body, *args, **kwargs)
    return wrapper

def parse_query_string(query_string: str):
    try:
        parsed_query = {key: value[0] for key, value in parse_qs(query_string).items()}
    except Exception:
        parsed_query = {}
    return parsed_query



class ParamsValidator:
    @classmethod
    def get_field_metadata(cls) -> Dict[str, Dict[str, Any]]:

        metadata = {}
        for field_name, annotated_type in cls.__annotations__.items():
            param_type, error_message = get_args(annotated_type)

            metadata[field_name] = {
                "type": param_type,
                "msg": error_message
            }
        
        return metadata

    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        params_after = deepcopy(params)
        validators = cls.get_field_metadata()

        for field_name, type_data in validators.items():
            param_type = type_data['type']
            error_msg = type_data['msg']
            try:
                params_after[field_name] = param_type(params[field_name])
            except Exception:
                del params_after
                raise UnprocessableEntityError(error_msg)

        return params_after
