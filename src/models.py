from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict, Optional, Union


@dataclass
class Request:
    query: dict[str, Any]
    get_body: Callable[[], Coroutine[None, None, dict]]
    headers: dict


@dataclass
class Response:
    status: int
    body: Any
    headers: Dict[str, str]
