from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict



@dataclass
class Request:
    query: dict[str, Any]
    get_body: Callable
    headers: dict


@dataclass
class Response:
    status: int
    body: Any
    headers: Dict[str, str]


class DotDict(dict):
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
