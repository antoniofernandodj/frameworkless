class HTTPException(Exception):
    def __init__(self, detail: str, code: int) -> None:
        self.code = code
        self.detail = detail
        super().__init__(detail, code)

    def json(self):
        return {
            "status": self.code,
            "body": {
                "detail": self.detail
            }
        }


# 4xx Client Errors
class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad Request") -> None:
        super().__init__(detail, 400)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(detail, 401)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(detail, 403)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Not Found") -> None:
        super().__init__(detail, 404)


class MethodNotAllowedError(HTTPException):
    def __init__(self, detail: str = "Method Not Allowed") -> None:
        super().__init__(detail, 405)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(detail, 409)


class GoneError(HTTPException):
    def __init__(self, detail: str = "Gone") -> None:
        super().__init__(detail, 410)


class UnprocessableEntityError(HTTPException):
    def __init__(self, detail: str = "Unprocessable Entity") -> None:
        super().__init__(detail, 422)


class TooManyRequestsError(HTTPException):
    def __init__(self, detail: str = "Too Many Requests") -> None:
        super().__init__(detail, 429)


# 5xx Server Errors
class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal Server Error") -> None:
        super().__init__(detail, 500)


class NotImplementedError(HTTPException):
    def __init__(self, detail: str = "Not Implemented") -> None:
        super().__init__(detail, 501)


class BadGatewayError(HTTPException):
    def __init__(self, detail: str = "Bad Gateway") -> None:
        super().__init__(detail, 502)


class ServiceUnavailableError(HTTPException):
    def __init__(self, detail: str = "Service Unavailable") -> None:
        super().__init__(detail, 503)


class GatewayTimeoutError(HTTPException):
    def __init__(self, detail: str = "Gateway Timeout") -> None:
        super().__init__(detail, 504)
