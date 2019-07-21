import typing

from starlette.authentication import BaseUser


class BaseAuthenticate:
    async def find_user(self, username: str) -> typing.Optional[BaseUser]:
        raise NotImplementedError

    async def verify_password(self, user: BaseUser, password: str) -> bool:
        raise NotImplementedError

    async def __call__(
        self, username: str, password: str
    ) -> typing.Optional[BaseUser]:
        user = await self.find_user(username=username)

        valid = await self.verify_password(user, password)
        if not valid:
            return None

        return user
