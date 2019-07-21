import inspect
import typing

from ..base.helpers import BaseAuthenticate
from ..passwords import BaseHasher

import orm

UserModel = typing.Type[orm.Model]


class ModelAuthenticate(BaseAuthenticate):
    _model: UserModel

    def __init__(
        self,
        model: typing.Union[UserModel, typing.Callable[[], UserModel]],
        hasher: BaseHasher,
        password_field: str = "password",
    ):
        if inspect.isclass(model) and issubclass(model, orm.Model):
            self._get_model = lambda: model
        else:
            assert inspect.isfunction(model)
            self._get_model = model
        self.hasher = hasher
        self.password_field = password_field

    @property
    def model(self) -> UserModel:
        try:
            return self._model
        except AttributeError:
            self._model = self._get_model()
            return self._model

    async def find_user(self, username: str) -> typing.Optional[orm.Model]:
        try:
            return await self.model.objects.get(username=username)
        except orm.NoMatch:
            return None

    async def verify_password(self, user: orm.Model, password: str):
        password_hash = getattr(user, self.password_field)
        valid = await self.hasher.verify(password, password_hash)

        if not valid:
            return False

        if self.hasher.needs_update(password_hash):
            new_hash = await self.hasher.make(password)
            await user.update(**{self.password_field: new_hash})

        return True
