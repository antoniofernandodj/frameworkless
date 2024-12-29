from src import App, SimpleLoggingMiddleware

app = SimpleLoggingMiddleware(App())
