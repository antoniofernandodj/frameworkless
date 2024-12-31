from abc import ABC
import re
from typing import Any, Callable, Tuple
class BaseRouter(ABC):

    routes: dict

    def match_route(self, method, path):
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


    def register_endpoints(self, endpoints: tuple):
        for endpoint in endpoints:
            data = self.register_endpoint(endpoint)
