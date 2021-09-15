import importlib
from typing import *
import jwt
import datetime
import config
from ..exceptions import AuthenticationFailed
from ..runtime import context
from ..tools import all_in
from .. import settings, logger
from .models import User, Session, RefreshToken, SessionUser
from .types import IJwtToken, IPermissions
from .tools import *
from .const import SETTINGS_JWT_EXPIRE


__all__ = [
    'authenticate',
    'create_session',
    'refresh_with_token',
    'drop_user_sessions_by_id',
    'drop_user_sessions_by_login',
    'permitted',
    'get_current_user',
    'is_logged_in'
]


_auth_backends_configured: List[str] = config.AUTH.get('backends', None)
if not _auth_backends_configured:
    _auth_backends_configured = ['local']
if not isinstance(_auth_backends_configured, (list, tuple)):
    raise RuntimeError("config.AUTH.backends must be List[str] of authentication backend names")

backends = {
    _n: importlib.import_module('.'.join(['system', 'aaa', 'auth', _n])) for _n in _auth_backends_configured
}


async def authenticate(username: str, password: str) -> User:
    """ Tries to authenticate the user using given username and password, with all available backends.

    :param username: the user, with or without '@' and a domain part
    :type username: str

    :param password: the password for the user
    :type password: str

    :return: a :class:`system.aaa.models.User` instance if succeed

    :raises AuthenticationFailed: if failed to authenticate
    """

    user: Optional[User]
    for backend in backends.values():
        user = await backend.authenticate(username, password)
        if user is not None:
            user.last_login = datetime.datetime.now()
            return user
    raise AuthenticationFailed


async def _create_jwt_token(user: User, session: Session) -> Tuple[str, datetime.datetime]:
    settings_: settings.SettingsCatalog = await settings.get('aaa')
    jwt_expire: int = settings_[SETTINGS_JWT_EXPIRE] * 60
    logger.debug(f"settings[SETTINGS_JWT_EXPIRE] = {jwt_expire}", "_create_jwt_token")

    exp: datetime.datetime
    if not jwt_expire:
        exp = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    else:
        exp = datetime.datetime.now() + datetime.timedelta(seconds=jwt_expire)

    payload: IJwtToken = {
        'user': str(user.id),
        'sess': session.token,
        'iat': datetime.datetime.now(),
        'exp': exp,
        'sub': 'token',
        'aud': config.AUTH['audience']
    }
    jwt_token: str = jwt.encode(payload, str(config.AUTH['secret']), algorithm='HS256')

    return jwt_token, exp


async def _create_refresh_token(user: User, session: Session) -> str:
    token: str = random_token(strong=True)
    await RefreshToken.create(
        token=token,
        user_id=user.id,
        session=session.token
    )
    return token


async def create_session(user: User) -> Tuple[str, str, datetime.datetime]:
    session: Session = await Session.create(user)

    jwt_token: str
    exp: datetime.datetime
    refresh_token: str

    jwt_token, exp = await _create_jwt_token(user, session)
    refresh_token = await _create_refresh_token(user, session)

    return jwt_token, refresh_token, exp


async def refresh_with_token(refresh_token: str) -> Tuple[User, str, str, datetime.datetime]:
    token: Optional[RefreshToken] = await RefreshToken.first(token=refresh_token)
    if token is None:
        raise AuthenticationFailed("Token has not been found")

    await token.delete()

    session: Optional[Session] = await Session.fetch(token.user_id, token.session)
    if session is None:
        raise AuthenticationFailed("Session has not been found")

    user: Optional[User] = await User.get(token.user_id)
    if user is None:
        raise AuthenticationFailed("User has not been found")

    jwt_token: str
    exp: datetime.datetime
    refresh_token: str

    jwt_token, exp = await _create_jwt_token(user, session)
    refresh_token = await _create_refresh_token(user, session)

    return user, jwt_token, refresh_token, exp


async def drop_user_sessions_by_id(user_id: str) -> None:
    """ Drops all user's sessions, whetever active or not, preventing the user to
    continue using the system immediately.

    :param user_id: the ID (:class:`User`->id) of the user
    :type user_id: str
    """

    sessions: List[Session] = await Session.fetch_all_for_user(user_id)
    [await sess.drop() for sess in sessions]


async def drop_user_sessions_by_login(login: str) -> None:
    """ Drops all user's sessions, whetever active or not, preventing the user to
    continue using the system immediately.

    :param login: the user's login (:class:`User`->login)
    :type login: str
    """

    user: Optional[User] = await User.first(login=login)
    if user is None:
        raise KeyError(f"aaa.User with login={login} does not exists")
    await drop_user_sessions_by_id(user.id)


def permitted(scopes: Union[str, Sequence[str]]) -> bool:
    """ Checks the current user has given permission scopes in his/her session.

    :param scopes: the scope (or scopes) required to be permitted for the user
    :type scopes: str, List(str)

    :return: True if the user has all permissions, False otherwise
    :rtype: bool
    """

    permissions: IPermissions = context['permissions']
    if not permissions:
        return False
    scopes: IPermissions = list(scopes) if isinstance(scopes, (list, tuple)) else [scopes, ]
    return all_in(scopes, permissions)


def get_current_user() -> Optional[SessionUser]:
    """ Returns the currently logged in user, if logged in, or None instead. """

    if not context:
        return None
    if 'user' not in context:
        return None
    if not isinstance(context['user'], SessionUser):
        return None
    return context['user']


def is_logged_in() -> bool:
    """ Returns True if the current request client is logged in, and False otherwise. """

    return get_current_user() is not None
