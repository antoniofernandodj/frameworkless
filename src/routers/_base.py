from abc import ABC
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from src.exceptions.http import MethodNotAllowedError
from src.utils import ENDPOINT_DATA, Route, make_response


MatchResult = Tuple[
    Optional[Callable],
    Optional[Dict[str, Any]]
]

class BaseRouter(ABC):

    routes: List[Dict[str, Any]]

    def match_route(
        self,
        request_method: str,
        request_path: str
    ) -> MatchResult:

        allowed_methods = set()
        method_not_allowed = False                        
        for item in self.routes:
            endpoint_method = item['method']
            endpoint_route = item['route']
            endpoint_controller = item['controller']

            if (m := endpoint_route.match(request_path)) is not None:
                allowed_methods.add(endpoint_method)
                if endpoint_method != request_method:
                    method_not_allowed = True
                    continue
                return endpoint_controller, m

        if request_method == "OPTIONS":
            return self.__get_options_handler(allowed_methods), {}

        if method_not_allowed:
            raise MethodNotAllowedError

        return None, None

    def register_endpoint(self, func, controller):
        url_prefix = str(getattr(controller, 'url_prefix', None) or '').rstrip('/')
        endpoint_data = getattr(func, ENDPOINT_DATA)
        method = endpoint_data['method']
        endpoint_pattern = endpoint_data['pattern']

        if not getattr(self, 'routes', None):
            self.routes = []

        r = Route(url_prefix + endpoint_pattern, method)
        print(r)
        self.routes.append({'method': method, 'route': r, 'controller': func})
        return endpoint_data

    def register_endpoints(self, endpoints: Union[tuple, list], controller):
        for endpoint in endpoints:
            self.register_endpoint(endpoint, controller)

    def register_controller(self, controller: Any):
        methods = []
        for attr in dir(controller):
            if attr.startswith("_"):
                continue
            method = getattr(controller, attr, None)
            if not callable(method):
                continue
            if getattr(method, ENDPOINT_DATA, None):
                methods.append(method)

        self.register_endpoints(methods, controller)

    def __get_options_handler(self, allowed_methods):
        async def endpoint_handler(*args, **kwargs):
            methods = sorted(allowed_methods | {"OPTIONS"})
            return make_response(204, None, {
                "Allow": ", ".join(methods),
                "Content-Length": "0",
            })

        return endpoint_handler


class APIRouter(BaseRouter):
    def __init__(self, controller):
        self.register_controller(controller)
