from src import App
from src.middlewares import (
    CORSMiddleware,
    HandleErrorMiddleware,
    RequestLoggingMiddleware,
    AuthenticationMiddleware
)


app = (
    App()
        .add_middleware(RequestLoggingMiddleware)
        .add_middleware(HandleErrorMiddleware)
        .add_middleware(CORSMiddleware)
        .add_middleware(AuthenticationMiddleware)
)
