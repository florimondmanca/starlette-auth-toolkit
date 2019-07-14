import typing

from starlette import authentication as auth

AuthResult = typing.Optional[typing.Tuple[auth.AuthCredentials, auth.BaseUser]]
