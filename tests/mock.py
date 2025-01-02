import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from src.models import Response


class RSGIHTTPProtocol:
    def __init__(self, body: Dict[str, Any]):
        self.body = body
        self.response: Optional[Response]

    async def __call__(self) -> bytes:
        try:
            return json.dumps(self.body).encode('utf-8')
        except:
            return str(self.body).encode('utf-8')
        
    def get_response(self) -> Response:
        assert self.response
        return self.response

    def __aiter__(self) -> Any: ...
    def response_empty(self, status: int, headers: List[Tuple[str, str]]): ...

    def response_str(self, status: int, headers: List[Tuple[str, str]], body: str):
        r = Response(status, body, { item[0]: item[1] for item in headers })
        self.response = r

    def response_bytes(self, status: int, headers: List[Tuple[str, str]], body: bytes): ...
    def response_file(self, status: int, headers: List[Tuple[str, str]], file: str): ...
    def response_stream(self, status: int, headers: List[Tuple[str, str]]) -> Any: ...


class RSGIHeaders:
    def __init__(self, items: Dict[str, str]):
        self.__items: List[Tuple[str, str]] = []
        for key, value in items.items():
            self.__items.append((key, value))

    def __contains__(self, key: str) -> bool:
        return any(k == key for k, _ in self.__items)

    def keys(self) -> List[str]:
        return [k for k, _ in self.__items]

    def values(self) -> List[str]:
        return [v for _, v in self.__items]

    def items(self) -> List[Tuple[str, str]]:
        return self.__items

    def get(self, key: str, default: Any = None) -> Any:
        for k, v in self.__items:
            if k == key:
                return v
        return default



@dataclass
class Scope:
    proto: str
    http_version: str
    rsgi_version: str
    server: str
    client: str
    scheme: str
    method: str
    path: str
    query_string: str
    headers: RSGIHeaders

    authority: Optional[str] = None



def make_rsgi_request(
    headers: Dict[str, str],
    body: Any,
    query_string: str,
    path: str,
    method: str
):

    scope = Scope(
        proto='',
        http_version='',
        rsgi_version='',
        server='',
        scheme='',
        client='',
        method=method,
        path=path,
        query_string=query_string,
        headers=RSGIHeaders(headers)
    )

    proto = RSGIHTTPProtocol(body)

    return scope, proto





class TestClient:
    def __init__(self, app) -> None:
        self.app = app

    async def get(self, path, body=None, query_string='', headers=None):
        return await self.mock_request(path, 'GET', body, query_string, headers)

    async def post(self, path, body=None, query_string='', headers=None):
        return await self.mock_request(path, 'POST', body, query_string, headers)

    async def put(self, path, body=None, query_string='', headers=None):
        return await self.mock_request(path, 'PUT', body, query_string, headers)

    async def delete(self, path, body=None, query_string='', headers=None):
        return await self.mock_request(path, 'DELETE', body, query_string, headers)

    async def mock_request(self, path, method, body, query_string, headers):
        headers = headers or {'content-type': 'application/json'}
        scope, proto = make_rsgi_request(
            headers=headers,
            body=body,
            query_string=query_string,
            path=path,
            method=method
        )
        await self.app.__rsgi__(scope, proto)  # type: ignore
        return proto.get_response()





def make_controller_request(query: dict, body: Any, headers = {}):
    
    from src.models import Request

    async def f(*args):
        return body

    return Request(query, f, headers)