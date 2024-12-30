from __future__ import annotations

from contextlib import suppress
from copy import deepcopy
from typing import Any, Dict, Literal, Optional, Tuple, Type, get_type_hints, get_args, Annotated
from functools import wraps
from typing import Callable, Coroutine, Dict, Any, List, Type, Union
from urllib.parse import parse_qs
from src.exceptions.http import UnprocessableEntityError


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

            if not isinstance(body, dict):
                raise UnprocessableEntityError('Must be a dict')

            body = params_validator.validate(body)
            return await func(self, params, body)

        return wrapper
    return decorator


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


def get_protocol_args(args):
    scope = args[0]
    send = None
    protocol_or_receive = None
    with suppress(Exception):
        protocol_or_receive = args[1]

    with suppress(Exception):
        send = args[2]

    return scope, protocol_or_receive, send


def is_rsgi_app(scope):
    return 'RSGI' in str(scope).upper() or 'GRANIAN' in str(scope).upper()


def headers_to_response(
    headers_dict: Dict[str, Any],
    mode: Literal['bytes', 'str'] = 'str'
) -> List[Union[Tuple[str, str], List[bytes]]]:

    result: List[Union[Tuple[str, str], List[bytes]]] = []
    for key, item in headers_dict.items():
        if mode == 'bytes':
            result.append([key.encode('utf-8'), item.encode('utf-8')])
        else:
            result.append((key, item))

    return result


def assure_tuples_of_str(data: List[Union[Tuple[str, str], List[bytes]]]) -> List[Tuple[str, str]]:
    result = []
    for item in data:
        if isinstance(item, tuple) and len(item) == 2 and all(isinstance(sub, str) for sub in item):
            result.append(item)
        elif isinstance(item, list) and all(isinstance(sub, bytes) for sub in item):
            try:
                converted = tuple(sub.decode("utf-8") for sub in item)
                if len(converted) == 2:
                    result.append(converted)
            except (UnicodeDecodeError, ValueError):
                pass
    return result



def print_app(app):
    apps = []
    current_app: Optional[Any] = app
    while 1:
        try:
            if current_app:
                apps.append(current_app)
                current_app = current_app.app
        except:
            break

    for app in apps:
        print(app)