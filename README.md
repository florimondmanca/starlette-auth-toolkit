# starlette-auth-toolkit

[![travis](https://travis-ci.org/florimondmanca/starlette-auth-toolkit.svg?branch=master)](https://travis-ci.org/florimondmanca/starlette-auth-toolkit)
[![pypi](https://badge.fury.io/py/starlette-auth-toolkit.svg)](https://pypi.org/project/starlette-auth-toolkit)
![python](https://img.shields.io/pypi/pyversions/starlette-auth-toolkit.svg)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)

Authentication backends and helpers for Starlette-based ASGI apps and frameworks.

> **Note**: documentation is in progress. In the meantime, feel free to [read the source code](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/starlette_auth_toolkit).

**Features**

- Database-agnostic.
- User model-agnostic.
- Built-in password hashing powered by [PassLib].
- Hash migration support.
- Built-in support for common authentication flows, including Basic and Bearer authentication.
- Support for multiple authentication backends.
- Easy integration with [`orm`].

[passlib]: https://passlib.readthedocs.io/en/stable/index.html
[`orm`]: https://github.com/encode/orm

**Contents**

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Base backends](#base-backends)
- [Backends](#backends)
- [Password hashers](#password-hashers)
- [Authentication helpers](#authentication-helpers)

## Installation

```bash
pip install starlette-auth-toolkit
```

## Quickstart

```python
import typing

from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse

from starlette_auth_toolkit.base.backends import BasicAuthBackend
from starlette_auth_toolkit.base.helpers import BaseAuthenticate
from starlette_auth_toolkit.cryptography import PBKDF2Hasher


# User model

class User(typing.NamedTuple):
    username: str
    password: str


# Password hasher

hasher = PBKDF2Hasher()


# Fake storage

USERS = {
    "alice": User(username="alice", password=hasher.make_sync("alicepwd")),
    "bob": User(username="bob", password=hasher.make_sync("bobpwd")),
}


# Authentication helper

class Authenticate(BaseAuthenticate):
    async def find_user(self, username: str):
        return USERS.get(username)

    async def verify_password(self, user: User, password: str):
        return await hasher.verify(password, user.password)


authenticate = Authenticate()


# Authentication backend

class BasicAuth(BasicAuthBackend):
    async def verify(
        self, username: str, password: str
    ) -> typing.Optional[User]:
        return await authenticate(username, password)


# Application

app = Starlette()
app.add_middleware(AuthenticationMiddleware, backend=BasicAuth())


@app.route("/")
@requires("authenticated")
async def home(request):
    """Example protected route."""
    return JSONResponse({"message": f"Hello, {request.user.username}!"})

```

Save this file as `app.py`. Then, assuming you have [uvicorn](https://www.uvicorn.org/) installed, run `$ uvicorn app:app` and make requests:

- Anonymous request:

```bash
curl http://localhost:8000 -i
```

```http
HTTP/1.1 401 Unauthorized
date: Sun, 21 Jul 2019 17:54:00 GMT
server: uvicorn
content-length: 52
content-type: text/plain; charset=utf-8

Could not authenticate with the provided credentials
```

- Authenticated request:

```bash
curl -u alice:alicepwd http://localhost:8000
```

```http
HTTP/1.1 200 OK
date: Sun, 21 Jul 2019 17:54:28 GMT
server: uvicorn
content-length: 27
content-type: application/json

{"message":"Hello, alice!"}
```

For a real-world example, [see here](https://github.com/florimondmanca/starlette-auth-toolkit/blob/master/tests/apps/example.py).

## Base backends

Base backends implement an **authentication flow**, but the exact implementation of credentials verification is left up to you. This means you can choose to perform a database query, use environment variables or private files, etc.

These backends grant a set of [scopes](https://www.starlette.io/authentication/#authcredentials) when authentication succeeds.

Although base backends are **user model agnostic**, we recommend you implement the interface specified by `starlette.authentication.BaseUser` (see also [Starlette authentication](https://www.starlette.io/authentication/)).

They are available at `starlette_auth_toolkit.base.backends`.

### `BasicAuthBackend`

Implementation of the [Basic authentication scheme](https://tools.ietf.org/html/rfc7617).

**Request header format**

```http
Authorization: Basic {credentials}
```

where `{credentials}` refers to the base64 encoding of `{username}:{password}`.

**Example**

```python
# myapp/auth.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit.base import backends

class BasicAuthBackend(backends.BasicAuthBackend):
    async def verify(self, username: str, password: str):
        # In practice, request the database to find the user associated
        # to `username`, and validate that its password hash matches the
        # given password.
        if (username, password) != ("bob", "s3kr3t"):
            return None
        return SimpleUser(username)
```

**Abstract methods**

- _async_ `.verify(self, username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

### `BearerAuthBackend`

Implementation of the [Bearer authentication scheme](https://tools.ietf.org/html/rfc6750), also known as _Token authentication_.

**Request header format**

```http
Authorization: Bearer {token}
```

**Example**

```python
# myapp/auth.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit.base import backends

class BearerAuthBackend(backends.BearerAuthBackend):
    async def verify(self, token: str):
        # In practice, request the database to find the token object
        # associated to `token`, and return its associated user.
        if token != "abcd":
            return None
        return SimpleUser("bob")
```

**Abstract methods**

- _async_ `.verify(self, token: str) -> Optional[BaseUser]`

  If `token` refers to a valid token, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

## Backends

Authentication backends listed here are ready-to-use implementations and are available in the `backends` module.

### `MultiAuth`

This backend allows you to support multiple authentication methods in your application. `MultiAuth` attempts authenticating using the given `backends` in order until one succeeds (or all fail).

**Example**

```python
from starlette_auth_toolkit.backends import MultiAuth

from myproject.auth import TokenAuth, BasicAuth  # TODO

# Allow to authenticate using either a token or username/password credentials.
backend = MultiAuth([TokenAuth(), BasicAuth()])
```

**Parameters**

- `backends` (`List[AuthBackend]`): a list of authentication backends, which determines which authentication methods clients can use to authenticate.

**Scopes**

- `authenticated`

## Password hashers

This package provides password hashing utilities built on top of [PassLib].

### Usage

- Asynchronous: `await .make()` / `await .verify()` (hashing and verification occurs in the threadpool)

```python
import asyncio
from starlette_auth_toolkit.cryptography import PBKDF2Hasher

async def main():
    # Instanciate a hasher:
    hasher = PBKDF2Hasher()

    # Hash a password:
    pwd = await hasher.make("hello")

    # Verify a password against a known hash:
    assert await hasher.verify("hello", pwd)

# Python 3.7+
asyncio.run(main())
```

- Blocking: `.make_sync()` / `.verify_sync()`

```python
from starlette_auth_toolkit.cryptography import PBKDF2Hasher

# Instanciate a hasher:
hasher = PBKDF2Hasher()

# Hash a password
pwd = hasher.make_sync("hello")

# Verify a password against a known hash:
assert hasher.verify_sync("hello", pwd)
```

### Hash migration (Advanced)

If you need to change the hash algorithm (say from PBKDF2 to Argon2), you will typically want to keep support for existing hashes, but rehash them with the new algorithm as soon as possible.

`MultiHasher` was designed to solve this problem:

```python
from starlette_auth_toolkit.cryptography import Argon2Hasher, PBKDF2Hasher, MultiHasher

hasher = MultiHasher([Argon2Hasher(), PBKDF2Hasher()])
```

The above `hasher` will use Argon2 when hashing new passwords, but will be able to verify hashes created using either Argon2 or PBKDF2.

To detect whether a hash needs rehashing, use `.needs_update()`:

```python
valid = await hasher.verify(pwd, pwd_hash)

if hasher.needs_update(pwd_hash):
    new_hash = await hasher.make(pwd)
    # TODO: store new hash

# ...
```

> **Note**: calling `.needs_update()` at anytime other than just after calling `.verify()` will raise a `RuntimeError`.

### Available hashers

| Name           | Requires      | PassLib algorithm |
| -------------- | ------------- | ----------------- |
| `PBKDF2Hasher` |               | `pbkdf2_sha256`   |
| `CryptHasher`  |               | `sha256_crypt`    |
| `BCryptHasher` | `bcrypt`      | `bcrypt`          |
| `Argon2Hasher` | `argon2-cffi` | `argon2`          |
| `MultiHasher`  |               | N/A               |

For advanced use cases, use `Hasher` and pass one of the algorithms listed in [passlib.hash](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html):

```python
from starlette_auth_toolkit.cryptography import Hasher

hasher = Hasher(algorithm="pbkdf2_sha512")
```

## Authentication helpers

Web applications often need to exchange user credentials (username and password) against the actual user.

Such an exchange is typically implemented as an `authenticate` utility function:

```python
user = await authenticate(username, password)
```

Helpers listed here make it easier to build a secure `authenticate` utility function, which you can then reuse when building your authentication backends.

### `base.helpers.BaseAuthenticate`

Base class for authentication helpers.

**Abstract methods**

- _async_ `.find_user(self, username: str) -> Optional[BaseUser]`

  Return the user associated to `username`, or `None` if none exist.

- _async_ `.verify_password(self, user: BaseUser, password: str) -> bool`

  Given a user, check that the given `password` is valid.
  For example, compare the given `password` against the user's password hash.

**Methods**

- _async_ `.__call__(self, username: str, password: str) -> Optional[BaseUser]`

  Authenticate a user using the following algorithm:

  1. Find a `user` using `.find_user()`
  2. Verify the password using `.verify_password()`
  3. Return `user` if it exists and the password is valid, and `None` otherwise.

### `contrib.orm.ModelAuthenticate`

A ready-to-use implementation of `BaseAuthenticate` using an `orm` user model.

**Note**: [`orm`] must be installed to use this helper.

**Example**

```python
from starlette.applications import Starlette
from starlette_auth_toolkit.contrib.orm import ModelAuthenticate
from starlette_auth_toolkit.cryptography import PBKDF2Hasher

from myproject.models import User  # DIY

hasher = PBKDF2Hasher()
authenticate = ModelAuthenticate(User, hasher=hasher)

app = Starlette()

@app.route("/")
async def home(request):
    data = await request.json()
    username, password = data["username"], data["password"]
    user: User = await authenticate(username, password)
    # ...
```

**Parameters**

- `model` (`orm.Model` or `() -> orm.Model`): the user model (or a callable for lazy loading).
- `hasher` (`BaseHasher`): a [password hasher](#password-hashers) — the same one used to hash user passwords.
- `password_field` (`str`, optional): field where password hashes are stored on user objects. Defaults to `"password"`.

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CHANGELOG.md).

## License

MIT
