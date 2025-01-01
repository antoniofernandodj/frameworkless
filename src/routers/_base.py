from abc import ABC
import re
from typing import Any, Callable, Dict, Optional, Tuple, Union


MatchResult = Tuple[
    Optional[Callable],
    Optional[Dict[str, Any]]
]

class BaseRouter(ABC):

    routes: dict

    def match_route(self, method, path) -> MatchResult:
        for pattern, methods in self.routes.items():
            compiled_pattern = re.compile(pattern)
            match = compiled_pattern.match(path)
            
            if match and method in methods:
                return methods[method], match.groupdict()

        return None, None


    def register_endpoint(self, func):
        data = func.CONTROLLER_DATA
        method = data['method']
        pattern = data['pattern']

        if not getattr(self, 'routes', None):
            self.routes = {}

        if not self.routes.get(pattern):
            self.routes[pattern] = {}

        self.routes[pattern][method] = func
        return data


    def register_endpoints(self, endpoints: Union[tuple, list]):
        for endpoint in endpoints:
            self.register_endpoint(endpoint)

    def register_controller(self, controller: Any):
        methods = []
        for attr in dir(controller):
            if callable(getattr(controller, attr)) and not attr.startswith("_"):
                method = getattr(controller, attr)
                if getattr(method, 'CONTROLLER_DATA', None):
                    methods.append(method)

        self.register_endpoints(methods)
        print(f'Registered Controller: {type(controller).__name__}')


class APIRouter(BaseRouter):
    def __init__(self, controller):
        self.register_controller(controller)
