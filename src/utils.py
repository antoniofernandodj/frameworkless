from __future__ import annotations

from typing import TypeVar
from asyncio import iscoroutinefunction
from contextlib import suppress
from copy import deepcopy
import re
from typing import Any, Dict, Literal, Optional, Tuple, Type, get_type_hints, get_args, Annotated
from functools import wraps
from typing import Callable, Coroutine, Dict, Any, List, Type, Union
from urllib.parse import parse_qs
from src.domain.models._base import DomainModel
from src.exceptions.http import UnprocessableEntityError
from src.models import Response


T = TypeVar('T')


def make_response(*args) -> Response:

    body = None
    status = 200
    headers = {'content-type': 'application/json'}

    for i, arg in enumerate(args):

        if isinstance(arg, DomainModel):
            body = {
                key: value for key, value
                in arg.to_dict().items()
                if 'instance_state' not in key
            }

        if isinstance(arg, int):
            status = arg

        if isinstance(arg, dict):
            if i == 0:
                body = arg
            else:
                headers.update(arg)

        if isinstance(arg, str):
            body = arg

    return Response(
        status,
        None if status == 204 else body,
        headers
    )


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
    def validate(cls, params: T) -> T:
        params_after = deepcopy(params)
        validators = cls.get_field_metadata()

        for field_name, type_data in validators.items():
            param_type = type_data['type']
            error_msg = type_data['msg']
            try:
                params_after[field_name] = param_type(params[field_name])  # type: ignore
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


def assure_tuples_of_bytes(data: List[Union[Tuple[bytes, bytes], List[str]]]) -> List[Tuple[bytes, bytes]]:
    result = []
    for item in data:
        if isinstance(item, tuple) and len(item) == 2 and all(isinstance(sub, bytes) for sub in item):
            result.append(item)
        elif isinstance(item, list) and all(isinstance(sub, str) for sub in item):
            try:
                converted = tuple(sub.encode("utf-8") for sub in item)
                if len(converted) == 2:
                    result.append(converted)
            except (UnicodeEncodeError, ValueError):
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
        print(f'app: {app}')



class Route:
    def __init__(self, path: str, endpoint: Callable):
        self.path = path
        self.endpoint = endpoint
        self.pattern, self.param_names = self._compile_path(path)

    def __str__(self):
        return f'Route(path="{self.path}", pattern="{self.pattern}")'
    
    def __repr__(self):
        return f'Route(path="{self.path}", pattern="{self.pattern}")'

    def _compile_path(self, path: str) -> Tuple[re.Pattern, List[Dict[str, str]]]:
        param_names = []
        regex = re.sub(
            r"<(\w+):([a-zA-Z0-9_\[\]-]+)>",
            lambda m: self._convert_placeholder(m, param_names),
            path
        )

        return re.compile(f"^{regex}$"), param_names

    def _convert_placeholder(
        self,
        match: re.Match,
        param_names: List[Dict[str, str]]
    ) -> str:
        
        name, typ = match.groups()
        param_names.append({'name': name, 'type': typ})

        if typ == "int":
            result = r"(\d+)"
        elif typ == "str":
            result = r"([^/]+)"
        elif typ == "float":
            result = r"(\d+\.\d+)"
        elif typ == 'list':
            result = r"((?:[^/]+,)*[^/]+)"
        elif typ == 'list[int]':
            result = r"((?:\d+,)*\d+)"
        elif typ == 'list[float]':
            result = r"((?:\d+\.\d+,)*\d+\.\d+)"
        elif typ == 'list[str]':
            result = r"((?:[^/]+,)*[^/]+)"
        elif typ == 'dict':
            result = r"((?:[^/]+,)*[^/]+)"
        else:
            raise ValueError(f"Tipo de parâmetro desconhecido: {typ}")


        return result


    def match(self, path: str) -> Union[None, Dict[str, Any]]:
        matched = self.pattern.search(path)

        if not matched:
            return None

        g: Dict[str, type] = {
            'int': int,
            'str': str,
            'float': float,
            'list': list,
            'list[int]': list[int],
            'list[float]': list[float],
            'list[str]': list[str],
            'dict': dict
        }

        values = {}
        for i, param in enumerate(self.param_names):
            typ = g[param['type']]
            name = param['name']

            mg = matched.groups()
            if typ == int:
                value = typ(mg[i])
            elif typ == float:
                value = typ(mg[i])
            elif typ == list:
                value = mg[i].split(',')
            elif typ == list[int]:
                value = [int(x) for x in mg[i].split(',')]
            elif typ == list[float]:
                value = [float(x) for x in mg[i].split(',')]
            elif typ == list[str]:
                value = mg[i].split(',')
            elif typ == dict:
                value = self._parse_dict(mg[i])
            elif typ == str:
                value = typ(mg[i])
            else:
                value = typ(mg[i])

            values[name] = value
    
        return values

    def _parse_dict(self, dict_string: str) -> Dict[str, Any]:
        items = dict_string.split(',')

        result = {}
        for item in items:
            key_value = item.split('=')
            if len(key_value) == 2:
                key, value = key_value
                result[key.strip()] = value.strip()
            else:
                raise ValueError(f"Formato de dicionário inválido: {item}")

        return result


def get(pattern: str):
    def decorator(func: Callable):

        func.CONTROLLER_DATA = {
            'method': 'GET', 'pattern': pattern
        }

        @wraps(func)
        async def inner(self, *args, **kwargs):
            if iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        
        return inner
    return decorator

def post(pattern: str):
    def decorator(func: Callable):

        func.CONTROLLER_DATA = {
            'method': 'POST', 'pattern': pattern
        }

        @wraps(func)
        async def inner(self, *args, **kwargs):
            if iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        
        return inner
    return decorator

def patch(pattern: str):
    def decorator(func: Callable):

        func.CONTROLLER_DATA = {
            'method': 'PATCH', 'pattern': pattern
        }

        @wraps(func)
        async def inner(self, *args, **kwargs):
            if iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        
        return inner
    return decorator

def put(pattern: str):
    def decorator(func: Callable):

        func.CONTROLLER_DATA = {
            'method': 'PUT', 'pattern': pattern
        }

        @wraps(func)
        async def inner(self, *args, **kwargs):
            if iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        
        return inner
    return decorator

def delete(pattern: str):
    def decorator(func: Callable):

        func.CONTROLLER_DATA = {
            'method': 'DELETE', 'pattern': pattern
        }

        @wraps(func)
        async def inner(self, *args, **kwargs):
            if iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        
        return inner
    return decorator
