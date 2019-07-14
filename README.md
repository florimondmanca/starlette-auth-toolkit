# starlette-auth-toolkit

[![travis](https://travis-ci.org/florimondmanca/starlette-auth-toolkit.svg?branch=master)](https://travis-ci.org/florimondmanca/starlette-auth-toolkit)
[![pypi](https://badge.fury.io/py/starlette-auth-toolkit.svg)](https://pypi.org/project/starlette-auth-toolkit)
![python](https://img.shields.io/pypi/pyversions/starlette-auth-toolkit.svg)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)

Authentication backends and helpers for Starlette-based apps and frameworks.

**Note**: documentation is in progress — in the meantime, feel free to read the source code!

## Installation

```bash
pip install starlette-auth-toolkit
```

**Note**: you need to [install Starlette](https://www.starlette.io/#installation) yourself.

## Base backends

Base backends implement an **authentication flow**, but the exact implementation of credentials verification is left up to you. This means you can choose to perform a database query, use environment variables or private files, etc.

These backends grant a set of [scopes](https://www.starlette.io/authentication/#authcredentials) when authentication succeeds.

Base backends are **user model agnostic**, although we recommend you implement the interface specified by `starlette.authentication.BaseUser` (see also [Starlette authentication](https://www.starlette.io/authentication/)).

### `BasicAuthBackend`

Implementation of the [Basic authentication scheme](https://tools.ietf.org/html/rfc7617).

**Request header format**

```http
Authorization: Basic {credentials}
```

where `{credentials}` refers to the base64 encoding of `{username}:{password}`.

**Abstract methods**

- `.verify(self, username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

**Example**

```python
# myapp/auth.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit import backends

class BasicAuthBackend(backends.BasicAuthBackend):
    async def verify(self, username: str, password: str):
        # TODO: in practice, request the database to find the user associated
        # to `username`, and validate that its password hash matches the
        # given password.
        if (username, password) != ("guido", "s3kr3t"):
            return None
        return SimpleUser(username)
```

### `BearerAuthBackend`

Implementation of the [Bearer authentication scheme](https://tools.ietf.org/html/rfc6750).

> Note: this is sometimes also referred to as "Token authentication".

**Request header format**

```http
Authorization: Bearer {token}
```

**Abstract methods**

- `.verify(self, token: str) -> Optional[BaseUser]`

  If `token` refers to a valid token, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

**Example**

```python
# myapp/auth.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit import backends

class BearerAuthBackend(backends.BearerAuthBackend):
    async def verify(self, token: str):
        # TODO: in practice, request the database to find the token object
        # associated to `token`, and return its associated user.
        if token != "abcd":
            return None
        return SimpleUser("bob")
```

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CHANGELOG.md).

## License

MIT
