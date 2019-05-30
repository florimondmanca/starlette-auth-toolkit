# starlette-auth-toolkit

[![travis](https://img.shields.io/travis/florimondmanca/starlette-auth-toolkit.svg)](https://travis-ci.org/florimondmanca/starlette-auth-toolkit)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
![python](https://img.shields.io/pypi/pyversions/starlette-auth-toolkit.svg)
[![pypi](https://img.shields.io/pypi/v/starlette-auth-toolkit.svg)](https://pypi.org/project/starlette-auth-toolkit)
![license](https://img.shields.io/badge/license-MIT-green.svg)

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

### [Basic auth](https://tools.ietf.org/html/rfc7617)

**Abstract methods**

- `.verify(self, username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding user. Otherwise, return `None`.

**Scopes**

- `authenticated`

**Example**

```python
# myapp/auth.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit.backends import BaseBasicAuthBackend

class BasicAuthBackend(BaseBasicAuthBackend):
    async def verify(self, username: str, password: str):
        # TODO: you'd probably want to make a DB call here.
        if (username, password) != ("guido", "s3kr3t"):
            return None
        return SimpleUser(username)
```

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/starlette-auth-toolkit/tree/master/CHANGELOG.md).

## License

MIT
