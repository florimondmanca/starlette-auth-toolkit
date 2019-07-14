from starlette.authentication import AuthenticationError


class InvalidCredentials(AuthenticationError):
    def __init__(
        self,
        message: str = "Could not authenticate with the provided credentials",
    ):
        super().__init__(message)
