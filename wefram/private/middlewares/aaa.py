from typing import *
import jwt
from starlette.authentication import (
    AuthenticationBackend,
    BaseUser,
    AuthCredentials,
    AuthenticationError,
    UnauthenticatedUser
)
from starlette.requests import HTTPConnection
from starlette.middleware.authentication import AuthenticationMiddleware
from ... import logger, cli
from ...requests import is_static_path
from ...runtime import context


__all__ = [
    'AuthenticationCliMiddleware',
    'AuthenticationMiddleware',
    'ProjectAuthenticationBackend',
]


class AuthenticationCliMiddleware(cli.CliMiddleware):
    async def __call__(self, call_next: Callable) -> None:
        from ...models import Session

        context['is_authenticated'] = False
        context['user']: BaseUser = UnauthenticatedUser()
        context['permissions']: List[str] = []
        context['session']: Optional[Session] = None
        await call_next()


class ProjectAuthenticationBackend(AuthenticationBackend):
    def __init__(
            self,
            secret: str,
            schema: str = 'Bearer',
            algorithm: str = 'HS256',
            audience: str = None
    ):
        self.secret: str = secret
        self.schema: str = schema
        self.algorithm: str = algorithm
        self.audience: str = audience

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple['AuthCredentials', 'BaseUser']]:
        from ...models import Session, SessionUser

        context['is_authenticated'] = False
        context['user']: BaseUser = UnauthenticatedUser()
        context['permissions']: List[str] = []
        context['session']: Optional[Session] = None

        if is_static_path(conn.scope['path']):
            return

        if 'Authorization' not in conn.headers:
            return

        authorization: str = conn.headers['Authorization']
        if authorization == 'null':
            return

        if ' ' not in authorization:
            raise AuthenticationError("Invalid JWT authorization")

        schema: str
        token_hash: str
        payload: dict

        try:
            schema, token_hash = authorization.split(' ', 1)
        except ValueError:
            return

        if token_hash == 'null':
            return

        if schema != self.schema:
            logger.debug("invalid jwt token, continuing as unauthenticated user")
            return

        try:
            payload = jwt.decode(
                token_hash, key=self.secret, algorithms=[self.algorithm], audience=self.audience
            )

        except jwt.ExpiredSignatureError:
            # raise AuthenticationError("Expired JWT token")
            logger.debug("expired jwt token, continuing as unauthenticated user")
            return

        except jwt.InvalidTokenError:
            # raise AuthenticationError("Invalid JWT token")
            logger.debug("invalid jwt token, continuing as unauthenticated user")
            return

        session_token: str = payload['sess']
        user_id: str = payload['user']
        try:
            session: Optional[Session] = await Session.fetch(user_id, session_token)
        except FileNotFoundError:
            logger.debug("expired session for the given jwt token")
            return

        auth_scopes: List[str] = ['authenticated', ] + session.permissions
        auth_user: SessionUser = SessionUser(
            session=session,
            scopes=auth_scopes
        )

        context['is_authenticated'] = True
        context['user']: BaseUser = auth_user
        context['permissions']: List[str] = auth_scopes
        context['session']: Session = session

        if 'X-Avoid-Session-Touch' not in conn.headers:
            logger.debug(f"touching the session's last activity")
            await session.touch()

        return AuthCredentials(auth_scopes), auth_user

