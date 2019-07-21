import databases
import orm
import sqlalchemy
from starlette.authentication import BaseUser

from orm.models import QuerySet

database = databases.Database("sqlite:///tests/test.db", force_rollback=True)
metadata = sqlalchemy.MetaData()
from .resources import hasher


class UserQuerySet(QuerySet):
    async def create_user(self, *, password: str, **kwargs):
        kwargs["password"] = await hasher.make(password)
        return await self.create(**kwargs)


class User(BaseUser, orm.Model):
    __tablename__ = "user"
    __database__ = database
    __metadata__ = metadata

    objects = UserQuerySet()

    id = orm.Integer(primary_key=True)
    username = orm.String(max_length=128)
    password = orm.String(max_length=128)

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def is_authenticated(self) -> bool:
        return True


class Token(orm.Model):
    __tablename__ = "token"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    token = orm.String(max_length=256)
    user = orm.ForeignKey(to=User, allow_null=False)


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)
