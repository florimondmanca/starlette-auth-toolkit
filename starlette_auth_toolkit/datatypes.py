import typing

from starlette.authentication import AuthCredentials, BaseUser

AuthResult = typing.Optional[typing.Tuple[AuthCredentials, BaseUser]]
