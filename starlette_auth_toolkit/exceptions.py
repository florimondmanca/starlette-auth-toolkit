from starlette.authentication import AuthenticationError


class InvalidCredentials(AuthenticationError):
    def __init__(self, message, scheme: str = None):
        super().__init__(message)
        self.scheme = scheme
