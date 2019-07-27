import inspect
import typing

import orm

from ..base.backends import BaseBasicAuth
from ..cryptography import BaseHasher

_UserModel = typing.Type[orm.Model]
_User = orm.Model


class ModelBasicAuth(BaseBasicAuth):
    _model: _UserModel

    def __init__(
        self,
        model: typing.Union[_UserModel, typing.Callable[[], _UserModel]],
        *,
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
    def model(self) -> _UserModel:
        try:
            return self._model
        except AttributeError:
            self._model = self._get_model()
            return self._model

    async def find_user(self, username: str) -> typing.Optional[_User]:
        try:
            return await self.model.objects.get(username=username)
        except orm.NoMatch:
            return None

    async def verify_password(self, user: _User, password: str):
        password_hash = getattr(user, self.password_field)
        valid = await self.hasher.verify(password, password_hash)

        if not valid:
            return False

        if self.hasher.needs_update(password_hash):
            new_hash = await self.hasher.make(password)
            await user.update(**{self.password_field: new_hash})

        return True
