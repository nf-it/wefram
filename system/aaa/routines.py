from typing import *
import jwt
import datetime
import config
from ..exceptions import AuthenticationFailed
from ..requests import context
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
    'permitted',
    'get_current_user'
]


async def authenticate(username: str, password: str) -> User:
    user: Optional[User] = await User.first(login=username)
    if user is None:
        raise AuthenticationFailed
    if not test_password(password, user.secret):
        raise AuthenticationFailed
    user.last_login = datetime.datetime.now()
    return user


async def _create_jwt_token(user: User, session: Session) -> Tuple[str, datetime.datetime]:
    settings_: settings.SettingsCatalog = await settings.get('aaa')
    print(settings_)
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
    RefreshToken.create(
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


def permitted(scopes: [str, Sequence[str]]) -> bool:
    permissions: IPermissions = context['permissions']
    if not permissions:
        return False
    scopes: IPermissions = list(scopes) if isinstance(scopes, (list, tuple)) else [scopes, ]
    return all_in(scopes, permissions)


def get_current_user() -> Optional[SessionUser]:
    if not context:
        return None
    if 'user' not in context:
        return None
    if not isinstance(context['user'], SessionUser):
        return None
    return context['user']

