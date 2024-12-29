from __future__ import annotations

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


def validate_params(required_params: Union[Dict[str, Any], ParamsValidator]) -> Callable:

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self,
            params: Dict[str, Any],
            body: Union[List[Any], Dict[str, Any], Coroutine]
        ) -> Dict[str, Any]:

            nonlocal required_params
            if isinstance(required_params, ParamsValidator):
                required_params = required_params.to_dict()

            for param, param_data in required_params.items():
                param_type = param_data['type']
                error_message = param_data['msg']
                if param not in params:
                    raise UnprocessableEntityError(error_message)
                else:
                    params[param] = param_type(params[param])
            return await func(self, params, body)
        return wrapper
    return decorator


def validate_body(required_body_keys: Union[Dict[str, Any], ParamsValidator]) -> Callable:

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self,
            params: Dict[str, Any],
            body: Union[List[Any], Dict[str, Any], Coroutine]
        ) -> Dict[str, Any]:

            if not isinstance(body, (dict, list)):
                body = await parse_body(body)

            nonlocal required_body_keys
            if isinstance(required_body_keys, ParamsValidator):
                required_body_keys = required_body_keys.to_dict()

            for param, param_data in required_body_keys.items():
                param_type = param_data['type']
                error_message = param_data['msg']
                if param not in body:
                    raise UnprocessableEntityError(error_message)
                else:
                    params[param] = param_type(params[param])

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
    def __init__(self) -> None:
        self.validators: List[Dict[str, Any]] = []

    def add(self, param_name: str, param_type: Type, msg: str):
        self.validators.append({
            "param_name": param_name,
            "type": param_type,
            "msg": msg
        })

        return self

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        validation_dict = {}
        for validator in self.validators:
            validation_dict[validator["param_name"]] = {
                "type": validator["type"],
                "msg": validator["msg"]
            }
        return validation_dict