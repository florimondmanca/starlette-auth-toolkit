# starlette-auth-toolkit

Authentication backends and helpers for Starlette-based apps and frameworks.

**Note**: documentation is in progress — in the meantime, feel free to read the source code!

## Installation

> TODO

## Usage

### Base backends

Base backends implement an authentication flow, but leave the verification of credentials up to you. This means you can use them to perform verification against any credentials storage backend, e.g. a database, environment variables, a private file, etc.

**Note**: please refer to the [Starlette authentication documentation](https://www.starlette.io/authentication/) for general information on using Starlette authentication backends.

#### [Basic auth](https://tools.ietf.org/html/rfc7617)

**Abstract methods**

- `.verify(username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding Starlette `BaseUser` instance (or a subclass thereof). Otherwise, return `None`.

**Example usage**

```python
# myapp/backends.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit.backends import BaseBasicAuthBackend

class BasicAuthBackend(BaseBasicAuthBackend):
    async def verify(self, username: str, password: str):
        # TODO: you'd probably want to make a DB call here.
        if (username, password) != ("guido", "s3kr3t"):
            return None
        return SimpleUser(username)
```

## License

MIT
