from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict, Optional, TYPE_CHECKING, Type


if TYPE_CHECKING:
    from src.utils import ParamsValidator


@dataclass
class Request:
    query: dict[str, Any]
    get_body: Callable[[Optional[Type[ParamsValidator]]], Coroutine[Any, Any, Optional[DotDict]]]
    headers: dict


@dataclass
class Response:
    status: int
    body: Any
    headers: Dict[str, str]


class DotDict(dict):
    """Um dicionário que permite o acesso usando notação de ponto."""
    
    def __getattr__(self, name):
        """Permite acessar a chave do dicionário com notação de ponto."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """Permite adicionar ou atualizar itens no dicionário com notação de ponto."""
        self[name] = value
    
    def __delattr__(self, name):
        """Permite deletar uma chave do dicionário com notação de ponto."""
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
