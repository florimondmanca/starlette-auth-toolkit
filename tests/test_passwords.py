import pytest

from starlette_auth_toolkit.cryptography import (
    CryptHasher,
    Hasher,
    MultiHasher,
    PBKDF2Hasher,
    BCryptHasher,
    Argon2Hasher,
)

pytestmark = pytest.mark.asyncio


pbkdf2 = PBKDF2Hasher()
bcrypt = BCryptHasher()
argon2 = Argon2Hasher()
crypt = CryptHasher()
HASHERS = [pbkdf2, bcrypt, argon2, crypt]


@pytest.mark.slow
@pytest.mark.parametrize("hasher", HASHERS)
async def test_simple_hasher(hasher):
    hashed = await hasher.make("hello")
    assert await hasher.verify("hello", hashed)
    assert not hasher.needs_update(hashed)


@pytest.mark.slow
@pytest.mark.parametrize("hasher", HASHERS)
async def test_simple_hasher_sync(hasher):
    hashed = hasher.make_sync("hello")
    assert hasher.verify_sync("hello", hashed)
    assert not hasher.needs_update(hashed)


async def test_unknown_algorithm():
    with pytest.raises(ValueError) as ctx:
        Hasher("foo")
    error = str(ctx.value)
    assert "algorithm" in error


@pytest.fixture(name="hasher")
def fixture_hasher():
    return MultiHasher([pbkdf2, crypt])


@pytest.fixture(name="deprecated_hasher")
def fixture_deprecated_hasher(hasher):
    return hasher.hashers[1]


@pytest.mark.slow
async def test_multi_hasher(hasher):
    with pytest.raises(RuntimeError):
        hasher.needs_update("foo")

    hashed = await hasher.make("hello")
    assert await hasher.verify("hello", hashed)
    assert not hasher.needs_update(hashed)


@pytest.mark.slow
async def test_multi_hasher_update(hasher, deprecated_hasher):
    old_hash = await deprecated_hasher.make("hello")
    assert await hasher.verify("hello", old_hash)
    assert hasher.needs_update(old_hash)

    new_hash = await hasher.make("hello")
    assert await hasher.verify("hello", new_hash)
    assert not hasher.needs_update(new_hash)
