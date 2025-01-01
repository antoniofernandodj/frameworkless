from granian.rsgi import Scope
from granian._granian import RSGIHTTPProtocol
from typing import Callable, Dict, List, Any, Tuple, Union
import re


    
class JSONResponse:
    def __init__(self, content: Dict[str, Any], status: int = 200):
        self.content = content
        self.status = status

    def serialize(self):
        import json
        body = json.dumps(self.content)
        headers = [
            ('content-type', 'application/json'),
            ('content-length', str(len(body))),
        ]
        return self.status, headers, body



class Route:
    def __init__(self, path: str, endpoint: Callable):
        self.path = path
        self.endpoint = endpoint
        self.pattern, self.param_names = self._compile_path(path)

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


    
class StarletteRSGI:
    def __init__(self, routes: List[Route]):
        self.routes = routes

    async def __rsgi__(self, scope: Scope, protocol: RSGIHTTPProtocol):
        if scope.proto != 'http':
            protocol.response_str(
                status=400,
                headers=[('content-type', 'text/plain')],
                body="Unsupported protocol"
            )
            return

        path = scope.path
        for route in self.routes:
            match = route.match(path)

            if match is not None:
                try:
                    response = await route.endpoint(scope, **match)
                except:
                    response = route.endpoint(scope, **match)

                if isinstance(response, JSONResponse):
                    status, headers, body = response.serialize()
                    protocol.response_str(status, headers, body)
                else:
                    protocol.response_str(
                        status=500,
                        headers=[('content-type', 'text/plain')],
                        body="Unsupported response type"
                    )
                return

        protocol.response_str(
            status=404,
            headers=[('content-type', 'text/plain')],
            body="Not Found"
        )


async def homepage(request: Scope, names: list[str]):
    print(request)
    for name in names:
        print(f'Hello to {name}!')
    return JSONResponse({"hello": "world"})


async def homepage2(request: Scope, names: dict[str, str]):
    print(names)
    return JSONResponse(names)


app = StarletteRSGI(routes=[
    Route(f'/hello/<names:list[str]>', homepage),
    Route(f'/hello2/<names:dict>', homepage2)
])
