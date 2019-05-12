# starlette-auth-toolkit

Authentication backends and helpers for your Starlette-based apps and frameworks.

> Documentation is in progress — in the meantime, feel free to read the source code!

## Installation

> TODO

## Base backends

Base backends implement an authentication flow, but leave the verification of credentials up to you. This means you can use them to perform verification against any credential store, e.g. a database.

**Note**: please refer to the [Starlette authentication documentation](https://www.starlette.io/authentication/) for general information on using Starlette authentication backends.

### [Basic auth](https://tools.ietf.org/html/rfc7617)

**Abstract methods**

- `.check_user(username: str, password: str) -> Optional[BaseUser]`

  If `username` and `password` are valid, return the corresponding Starlette `BaseUser` instance (or a subclass thereof). Otherwise, return `None`.

#### Example usage

```python
# myapp/backends.py
from starlette.authentication import SimpleUser  # or a custom user model
from starlette_auth_toolkit.backends import BaseBasicAuthBackend

class BasicAuthBackend(BaseBasicAuthBackend):
    async def check_user(self, username: str, password: str):
        # TODO: you'd probably want to make a DB call here.
        if (username, password) != ("guido", "s3kr3t"):
            return None
        return SimpleUser(username)
```

## License

MIT
