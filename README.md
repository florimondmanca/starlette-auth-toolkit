# starlette-auth-toolkit

[![travis](https://travis-ci.org/florimondmanca/starlette-auth-toolkit.svg?branch=master)](https://travis-ci.org/florimondmanca/starlette-auth-toolkit)
[![pypi](https://badge.fury.io/py/starlette-auth-toolkit.svg)](https://pypi.org/project/starlette-auth-toolkit)
![python](https://img.shields.io/pypi/pyversions/starlette-auth-toolkit.svg)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)

Authentication backends and helpers for Starlette-based apps and frameworks.

**Note**: documentation is in progress — in the meantime, feel free to read the source code!

**Contents**

- [Installation](#installation)
- Usage:
  - [Base backends](#base-backends)
  - [Password hashers](#password-hashers)

## Installation

```bash
pip install starlette-auth-toolkit
```

**Note**: you need to [install Starlette](https://www.starlette.io/#installation) yourself.

## Base backends

Base backends implement an **authentication flow**, but the exact implementation of credentials verification is left up to you. This means you can choose to perform a database query, use environment variables or private files, etc.

These backends grant a set of [scopes](https://www.starlette.io/authentication/#authcredentials) when authentication succeeds.

Base backends are **user model agnostic**, although we recommend you implement the interface specified by `starlette.authentication.BaseUser` (see also [Starlette authentication](https://www.starlette.io/authentication/)).

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

- `.verify(self, username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

### `BearerAuthBackend`

Implementation of the [Bearer authentication scheme](https://tools.ietf.org/html/rfc6750).

> Note: this is sometimes also referred to as "Token authentication".

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

- `.verify(self, token: str) -> Optional[BaseUser]`

  If `token` refers to a valid token, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

## Password hashers

This package provides password hashing utilities built on top of [PassLib](https://passlib.readthedocs.io/en/stable/index.html).

### Usage

- Asynchronous: `await .make()` / `await .verify()` (hashing and verification occurs in the threadpool)

```python
import asyncio
from starlette_auth_toolkit.passwords import PBKDF2Hasher

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
from starlette_auth_toolkit.passwords import PBKDF2Hasher

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
from starlette_auth_toolkit.passwords import Argon2Hasher, PBKDF2Hasher, MultiHasher

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

For advanced use cases, use `Hasher` and pass one of the algorithms listed in [passlib.hash](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html):

```python
from starlette_auth_toolkit.passwords import Hasher

hasher = Hasher(algorithm="pbkdf2_sha512")
```

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CHANGELOG.md).

## License

MIT
