from src import App
from src.utils import print_app
from src.middlewares import (
    CORSMiddleware2,
    HandleErrorMiddleware,
    RequestLoggingMiddleware,
    AuthenticationMiddleware
)


# print_app(app)


app = (
    App()
        # .add_middleware(CORSMiddleware2, ['localhost', '127.0.0.1'])
        # .add_middleware(RequestLoggingMiddleware)
        # .add_middleware(AuthenticationMiddleware)
        # .add_middleware(HandleErrorMiddleware)
)
