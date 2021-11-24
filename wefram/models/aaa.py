from typing import *
from dataclasses import dataclass
import datetime
from starlette.authentication import BaseUser
from ..private.const.aaa import SETTINGS_SESSION_LIFETIME
from .. import ds
from ..tools import json_decode, json_encode, rerekey_snakecase_to_lowercamelcase


__all__ = [
    'RefreshToken',
    'Session',
    'User',
    'Role',
    'SessionLog',
    'SessionUser'
]


class RefreshToken(ds.Model):
    token = ds.Column(ds.String(128), nullable=False, primary_key=True)
    user_id = ds.Column(ds.UUID(), ds.ForeignKey('systemUser.id', ondelete='CASCADE'), nullable=False)
    session = ds.Column(ds.String(64), nullable=False)
    created = ds.Column(ds.DateTime(True), nullable=False, default=datetime.datetime.now)


class UsersRoles(ds.Model):
    user_id = ds.Column(ds.UUID(), ds.ForeignKey('systemUser.id', ondelete='CASCADE'))
    role_id = ds.Column(ds.UUID(), ds.ForeignKey('systemRole.id', ondelete='CASCADE'))
    _pk = ds.PrimaryKeyConstraint(user_id, role_id)


class User(ds.Model):
    id = ds.UUIDPrimaryKey()
    login = ds.Column(ds.String(80), nullable=False, unique=True)
    secret = ds.Column(ds.Password(), nullable=False)
    locked = ds.Column(ds.Boolean(), default=False, nullable=False)
    available = ds.Column(ds.Boolean(), default=True, nullable=False)
    created_at = ds.Column(
        ds.DateTime(True),
        default=datetime.datetime.now,
        nullable=False
    )
    created_by = ds.Column(
        ds.UUID(),
        ds.ForeignKey('systemUser.id'),
        nullable=True,
        default=None
    )
    last_login = ds.Column(ds.DateTime(True), nullable=True, default=None)
    first_name = ds.Column(ds.String(100), nullable=False, default='')
    middle_name = ds.Column(ds.String(100), nullable=False, default='')
    last_name = ds.Column(ds.String(100), nullable=False, default='')
    timezone = ds.Column(ds.String(80), nullable=True, default=None)
    locale = ds.Column(ds.String(8), nullable=True, default=None)
    avatar = ds.Column(ds.Image('system.users'), nullable=True, default=None)
    properties = ds.Column(ds.JSONB(), default=lambda: dict())
    comments = ds.Column(ds.Text(), nullable=False, default='')
    email = ds.Column(ds.Email(), nullable=False, default='')
    roles = ds.relationship(
        ds.TheModel('Role'),
        secondary='systemUsersRoles',
        back_populates='users',
        lazy='selectin'
    )

    class Meta:
        caption_key = 'caption'
        repr_by = [
            'id',
            'login',
            'full_name'
        ]
        hidden = ['secret']
        include = ['full_name', 'display_name']
        findable = ['full_name', 'login']
        attributes_sets = {
            'session': [
                'id',
                'login',
                'first_name',
                'middle_name',
                'last_name',
                'display_name',
                'full_name',
                'locale',
                'timezone'
            ]
        }
        history = ds.History(enable=True, ignore=['last_login'], exclude=['last_login', 'secret'])

    @ds.hybrid_property
    def full_name(self) -> str:
        """ Returns the full name of the user, including non-empty first name,
        middle name and the last name.
        """
        return ' '.join([s for s in (self.first_name, self.middle_name, self.last_name) if s != ''])

    @full_name.expression
    def full_name(cls):
        return ds.func.concat_ws(' ', cls.first_name, cls.middle_name, cls.last_name)

    @ds.hybrid_property
    def display_name(self) -> str:
        """ Returns the shorter name of the user, including only non-empty
        the first and the last names.
        """
        return ' '.join([s for s in (self.first_name, self.last_name) if s])

    @display_name.expression
    def display_name(cls):
        return ds.func.concat_ws(' ', cls.first_name, cls.last_name)

    @ds.hybrid_property
    def caption(self) -> str:
        return ' '.join([s for s in (
            self.first_name, self.middle_name, self.last_name, f"[{self.login}]"
        )])

    @caption.expression
    def caption(cls) -> str:
        """ Returns caption which includes both login and full name. """
        return ds.func.concat_ws(
            ' ', cls.first_name, cls.middle_name, cls.last_name,
            ds.func.concat('[', cls.login, ']')
        )

    async def all_permissions(self) -> List[str]:
        """ Returns a list of all permission scope current logged in
        user is accessible to.
        """
        return await self.all_permissions_for(self.id)

    @classmethod
    async def all_permissions_for(cls, user_id: str) -> List[str]:
        user: Optional[User] = await cls.get(user_id)
        if user is None:
            raise KeyError(f"User[id={user_id}] has not been found")
        roles: List[Role] = user.roles

        permissions: Set[str] = set()
        for role in roles:
            role_perms = role.permissions
            if not role_perms:
                continue
            permissions = permissions.union(set(role_perms))

        return list(permissions)


class Role(ds.Model):
    id = ds.UUIDPrimaryKey()
    name = ds.Column(ds.Caption(), unique=True)
    permissions = ds.Column(ds.JSONB(none_as_null=True))
    users = ds.relationship(
        ds.TheModel('User'),
        secondary='systemUsersRoles',
        back_populates='roles',
        lazy='selectin'
    )

    class Meta:
        findable = ['name']


class SessionLog(ds.Model):
    id = ds.BigAutoIncrement()
    user_id = ds.Column(ds.UUID(), ds.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    ts = ds.Column(ds.DateTime(), nullable=False, default=datetime.datetime.now)
    extra = ds.Column(ds.JSONB())


@dataclass
class Session:
    token: str
    user: dict
    permissions: List[str]
    start_timestamp: datetime.datetime
    touch_timestamp: datetime.datetime

    @classmethod
    async def create(cls, user: User) -> 'Session':
        from ..aaa import random_token

        session = cls(
            token=random_token(),
            user=user.dict(set_name='session'),
            permissions=await user.all_permissions(),
            start_timestamp=datetime.datetime.now(),
            touch_timestamp=datetime.datetime.now()
        )
        await session.save()
        return session

    def as_json(self) -> dict:
        return {
            'user': rerekey_snakecase_to_lowercamelcase(self.user),
            'permissions': self.permissions
        }

    def jsonify(self) -> str:
        response: dict = {
            'token': self.token,
            'user': self.user,
            'permissions': self.permissions,
            'start_timestamp': self.start_timestamp.isoformat(timespec='seconds'),
            'touch_timestamp': self.touch_timestamp.isoformat(timespec='seconds')
        }
        return json_encode(response)

    async def save(self) -> None:
        from .. import settings

        rk: str = self.redis_key_for(self.user['id'], self.token)
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        await cn.set(rk, self.jsonify())
        await cn.expire(rk, ((await settings.get('aaa'))[SETTINGS_SESSION_LIFETIME] * 60))

    async def touch(self) -> None:
        self.touch_timestamp = datetime.datetime.now()
        await self.save()

    async def drop(self) -> None:
        rk: str = self.redis_key_for(self.user['id'], self.token)
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        await cn.delete(rk)

    @classmethod
    async def fetch(cls, user_id: str, token: str) -> 'Session':
        rk: str = cls.redis_key_for(user_id, token)
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        jsoned: Optional[str] = await cn.get(rk)
        if jsoned is None:
            raise FileNotFoundError(token)
        cached: dict = json_decode(jsoned)
        values: Dict[str, Any] = cached
        values['start_timestamp'] = datetime.datetime.fromisoformat(values['start_timestamp'])
        values['touch_timestamp'] = datetime.datetime.fromisoformat(values['touch_timestamp'])
        return cls(**values)

    @classmethod
    def redis_key_for(cls, user_id: str, token: str) -> str:
        return ':'.join(['aaa', 'session', user_id, token])

    @classmethod
    async def get_all_sessrks_for_user(cls, user_id: str) -> List[str]:
        rk: str = ':'.join(['aaa', 'session', user_id, '*'])
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        return [k.decode('utf-8') for k in await cn.keys(rk)]

    @classmethod
    async def fetch_all_for_user(cls, user_id: str) -> List['Session']:
        rks: List[str] = await cls.get_all_sessrks_for_user(user_id)
        if not rks:
            return []
        return [
            (await cls.fetch(user_id, rk.split(':')[-1])) for rk in rks
        ]


class SessionUser(BaseUser):
    def __init__(
            self,
            session: Session,
            scopes: List[str]
    ) -> None:
        self.session: Session = session
        self.user: dict = self.session.user
        self.scopes: List[str] = scopes

        self.user_id: str = str(self.user.get('id', ''))
        self.login: str = str(self.user.get('login', ''))
        self.first_name: str = str(self.user.get('first_name', ''))
        self.middle_name: str = str(self.user.get('middle_name', ''))
        self.last_name: str = str(self.user.get('last_name', ''))
        self.locale: Optional[str] = self.user.get('locale', None) or None
        self.timezone: Optional[str] = self.user.get('timezone', None) or None

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return ' '.join([s for s in (self.first_name, self.middle_name, self.last_name, f"[{self.user['login']}]") if s])

    def __str__(self) -> str:
        return f"SessionUser: login={self.user['login']}, id={self.user['id']}"

