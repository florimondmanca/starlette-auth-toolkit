import secrets
import string
import typing

from starlette.concurrency import run_in_threadpool

try:
    import passlib.hash as _hashers
    from passlib.ifc import PasswordHash
except ImportError:  # pragma: no cover
    _hashers = None  # type: ignore
    PasswordHash = None  # type: ignore


def generate_random_string(size: int = 32) -> str:
    return "".join(
        secrets.choice(generate_random_string.alphabet) for _ in range(size)
    )


generate_random_string.alphabet = string.ascii_letters + string.digits


class BaseHasher:
    async def make(self, secret: str) -> str:
        return await run_in_threadpool(self.make_sync, secret)

    async def verify(self, secret: str, hashed: str) -> bool:
        return await run_in_threadpool(self.verify_sync, secret, hashed)

    def make_sync(self, secret: str) -> str:
        raise NotImplementedError

    def verify_sync(self, secret: str, hashed: str) -> bool:
        raise NotImplementedError

    def needs_update(
        self, hashed: str  # pylint: disable=unused-argument
    ) -> bool:
        return False


class Hasher(BaseHasher):
    def __init__(self, algorithm: str):
        assert (
            _hashers is not None
        ), "'passlib' must be installed to use password hashers"
        self.algorithm = algorithm
        try:
            self._hasher: PasswordHash = getattr(_hashers, algorithm)
        except AttributeError as exc:
            raise ValueError(f"unknown algorithm: {algorithm}") from exc

    def make_sync(self, secret: str) -> str:
        return self._hasher.hash(secret)

    def verify_sync(self, secret: str, hashed: str) -> bool:
        return self._hasher.verify(secret, hashed)

    def needs_update(self, hashed: str) -> bool:
        return self._hasher.needs_update(hashed)

    def identify(self, hashed: str) -> bool:
        return self._hasher.identify(hashed)


class PBKDF2Hasher(Hasher):
    def __init__(self):
        super().__init__("pbkdf2_sha256")


# Requires `bcrypt`
class BCryptHasher(Hasher):
    def __init__(self):
        super().__init__("bcrypt")


# Requires `argon2-cffi`
class Argon2Hasher(Hasher):
    def __init__(self):
        super().__init__("argon2")


class CryptHasher(Hasher):
    def __init__(self):
        super().__init__("sha256_crypt")


class MultiHasher(BaseHasher):
    _dummy_secret = "dummysecret"

    def __init__(self, hashers: typing.List[Hasher]):
        if not hashers:
            raise ValueError("'hashers' should contain at least one hasher")
        self.hashers = hashers
        self._needs_update = None
        self._dummy_hash = self.make_sync(self._dummy_secret)

    @property
    def default_hasher(self) -> BaseHasher:
        return self.hashers[0]

    def make_sync(self, secret: str) -> str:
        return self.default_hasher.make_sync(secret)

    def verify_sync(self, secret: str, hashed: str) -> bool:
        self._needs_update = None

        for hasher in self.hashers:
            if hasher.identify(hashed):
                if self._needs_update is None:
                    self._needs_update = hasher.needs_update(hashed)
                return hasher.verify_sync(secret, hashed)
            self._needs_update = True

        # Verify dummy password to reduce vulnerability to timing attacks.
        self.default_hasher.verify_sync(self._dummy_secret, self._dummy_hash)

        return False

    def needs_update(self, hashed: str) -> bool:
        if self._needs_update is None:
            raise RuntimeError(
                "cannot call '.needs_update()' before calling '.verify()'"
            )
        needs_update, self._needs_update = self._needs_update, None
        return needs_update
