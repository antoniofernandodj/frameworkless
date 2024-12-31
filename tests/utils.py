from typing import Any


def mock_request(path: dict, query: dict, body: Any, headers = {}):
    
    from src.models import Request

    async def f():
        return body

    return Request(path, query, f, headers)