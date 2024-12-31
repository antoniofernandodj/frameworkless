from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Coroutine, Optional, Union


@dataclass
class Request:
    path_args: dict[str, Any]
    query: dict[str, Any]
    get_body: Callable[[], Coroutine[None, None, dict]]
    headers: dict
