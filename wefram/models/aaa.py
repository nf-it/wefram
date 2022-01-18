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
    """ The model stores the JWT refresh tokens used for renew expired JWT """

    token = ds.Column(ds.String(128), nullable=False, primary_key=True)
    user_id = ds.Column(ds.UUID(), ds.ForeignKey('systemUser.id', ondelete='CASCADE'), nullable=False)
    session = ds.Column(ds.String(64), nullable=False)
    created = ds.Column(ds.DateTime(True), nullable=False, default=datetime.datetime.now)


class UsersRoles(ds.Model):
    """ The junction model for assigning roles to user and vise versa """

    user_id = ds.Column(ds.UUID(), ds.ForeignKey('systemUser.id', ondelete='CASCADE'))
    role_id = ds.Column(ds.UUID(), ds.ForeignKey('systemRole.id', ondelete='CASCADE'))
    _pk = ds.PrimaryKeyConstraint(user_id, role_id)


class User(ds.Model):
    """ The main system user model describing users able to log in to the system. """

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
    def full_name(self):
        return ds.func.concat_ws(' ', self.first_name, self.middle_name, self.last_name)

    @ds.hybrid_property
    def display_name(self) -> str:
        """ Returns the shorter name of the user, including only non-empty
        the first and the last names.
        """
        return ' '.join([s for s in (self.first_name, self.last_name) if s])

    @display_name.expression
    def display_name(self):
        return ds.func.concat_ws(' ', self.first_name, self.last_name)

    @ds.hybrid_property
    def caption(self) -> str:
        return ' '.join([s for s in (
            self.first_name, self.middle_name, self.last_name, f"[{self.login}]"
        )])

    @caption.expression
    def caption(self) -> str:
        """ Returns caption which includes both login and full name. """
        return ds.func.concat_ws(
            ' ', self.first_name, self.middle_name, self.last_name,
            ds.func.concat('[', self.login, ']')
        )

    async def all_permissions(self) -> List[str]:
        """ Returns a list of all permission scope current logged-in
        user is accessible to.

        Example of the result:
        ['app1.permission1', 'app1.permission2', 'app2.some_permission']
        """

        return await self.all_permissions_for(self.id)

    @classmethod
    async def all_permissions_for(cls, user_id: str) -> List[str]:
        """ Returns a list of all permission scope the given user (by
        his/her ID) is accessible to.

        Example of the result:
        ['app1.permission1', 'app1.permission2', 'app2.some_permission']

        :param user_id: the ID of the user for which return permissions for
        :return: list of permissions
        """

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

    @classmethod
    async def update_locked_state(cls, state: bool, ids: List[str]) -> None:
        """ Updates the locked status for the given list of users. Users
        about to be given by their 'id'.

        :param state: The state to be set for all given users;
        :param ids: The list of corresponding users' IDs (UUIDs)
        """

        users: List[User] = await cls.all(cls.id.in_(ids))
        if not users:
            return

        for user in users:
            user.locked = state


class Role(ds.Model):
    """ The role model describing sets of permissions grouped by roles. """

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
        caption_key = 'name'
        findable = ['name']


class SessionLog(ds.Model):
    """ The journaling model stores all successful logins of users """

    id = ds.BigAutoIncrement()
    user_id = ds.Column(ds.UUID(), ds.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    ts = ds.Column(ds.DateTime(), nullable=False, default=datetime.datetime.now)
    extra = ds.Column(ds.JSONB())

    class Meta:
        order = '-ts'


@dataclass
class Session:
    """ The session class used in-memory as representation of the current
    (request-context) user's session. Not applies to the SQL database. """

    token: str
    user: dict
    permissions: List[str]
    start_timestamp: datetime.datetime
    touch_timestamp: datetime.datetime

    @classmethod
    async def create(cls, user: User) -> 'Session':
        """ Creates a new session for the given user (actual for the log-in
        time when user has successfully logged in to the system).
        The new created session saves to the in-memory storage (Redis) as
        result.

        :param user: The :class:~wefram.models.aaa.User: object
        :return: the :class:~wefram.models.aaa.Session: session object
        """

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
        """ Saves the current session object to the in-memory storage (Redis) giving
        all working processes ability to act with it. """

        from .. import settings

        rk: str = self.redis_key_for(self.user['id'], self.token)
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        await cn.set(rk, self.jsonify())
        await cn.expire(rk, ((await settings.get('aaa'))[SETTINGS_SESSION_LIFETIME] * 60))

    async def touch(self) -> None:
        """ Refreshes the last session activity timestamp in the in-memory storage. """

        self.touch_timestamp = datetime.datetime.now()
        await self.save()

    async def drop(self) -> None:
        """ Drops this session deleting it from the in-memory storage, preventing
        (if any) logged-in user from ability to continue work using this session. """

        rk: str = self.redis_key_for(self.user['id'], self.token)
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        await cn.delete(rk)

    @classmethod
    async def fetch(cls, user_id: str, token: str) -> 'Session':
        """ Fetches the session for the given user's ID and given session token.
        Returns the :class:~wefram.models.aaa.Session: object if the session
        exists, or raises FileNotFoundError otherwise.

        :param user_id: the :class:~wefram.models.aaa.User: 'id' of the user;
        :param token: the corresponding session token
        :return: the Session object, if the session exists
        :raises: FileNotFoundError if there is no session for given criteria
        """

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
        """ Return the Redis key name for the given user and token. The key will
        be combined with static prefix 'aaa:session' and corresponding
        user id and corresponding session token.

        Example:
        "aaa:session:1ab2fa10-d152-4ac9-9d06-1bfee423ce70:64478e7a965e4fb6a56327a45c03f282c0e745c2d5d64f96b0d0e73c483b64b0"

        :param user_id: the :class:~wefram.models.aaa.User: 'id' of the user;
        :param token: the corresponding session token
        :return: the corresponding Redis key
        """

        return ':'.join(['aaa', 'session', user_id, token])

    @classmethod
    async def get_all_sessrks_for_user(cls, user_id: str) -> List[str]:
        """ Fetches all present in the in-memory storage (Redis) sessions'
        keys (Redis keys) for the given user (by user's id). This gives
        an ability to fetch all sesssions for the given user.

        Example result:
        [
            "aaa:session:1ab2fa10-d152-4ac9-9d06-1bfee423ce70:64478e7a965e4fb6a56327a45c03f282c0e745c2d5d64f96b0d0e73c483b64b0",
            "aaa:session:1ab2fa10-d152-4ac9-9d06-1bfee423ce70:34478e74965e41b6a36327a45c6af282c0e7421255dacf96b540d0e73c483b64"
        ]

        :param user_id: the corresponding User.id for which about to fetch
            and list all keys
        :return: a list of redis keys of all sessions for the corresponding
            user
        """

        rk: str = ':'.join(['aaa', 'session', user_id, '*'])
        cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        return [k.decode('utf-8') for k in await cn.keys(rk)]

    @classmethod
    async def fetch_all_for_user(cls, user_id: str) -> List['Session']:
        """ Returns active sessions (:class:~wefram.models.aaa.Session: objects) for the
        given user by the corresponding ID.

        :param user_id: The ID of the user for which to get all sessions for
        :return: a list of Session objects
        """
        rks: List[str] = await cls.get_all_sessrks_for_user(user_id)
        if not rks:
            return []
        return [
            (await cls.fetch(user_id, rk.split(':')[-1])) for rk in rks
        ]


class SessionUser(BaseUser):
    """ The request-level session user used in the AAA context. """

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

