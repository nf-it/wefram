from typing import *
import datetime
import time
from .. import api, logger
from ..requests import Request, NoContentResponse, JSONResponse, HTTPException, context
from ..exceptions import AuthenticationFailed
from .wrappers import requires_authenticated
from .routines import authenticate, create_session, refresh_with_token
from .models import User, Session
from .types import ISession, IAuthorizationResponse
from .middleware import SessionUser


API_VER: int = 1


async def _auth_response(
        user: User,
        token: str,
        refresh_token: str,
        expire: datetime.datetime
) -> IAuthorizationResponse:
    return {
        'token': token,
        'refreshToken': refresh_token,
        'user': user.as_json(set_name='session'),
        'expire': expire.isoformat(timespec='seconds'),
        'permissions': await user.all_permissions()
    }


@api.handle_post('/authenticate', API_VER)
async def login(request: Request) -> JSONResponse:
    payload: Dict[str, str] = request.scope['payload']
    username: str = payload.get('username', None)
    password: str = payload.get('password', None)

    if not username or not password:
        logger.debug("no username or password", 'login')
        raise HTTPException(400)

    try:
        user: User = await authenticate(username, password)
    except AuthenticationFailed:
        time.sleep(2)
        logger.info(f"authentication failed for '{username}'", 'login')
        raise HTTPException(401)

    token: str
    refresh_token: str
    expire: datetime.datetime
    token, refresh_token, expire = await create_session(user)
    logger.info(f"successfully authenticated '{username}'", 'login')

    return JSONResponse(await _auth_response(
        user, token, refresh_token, expire
    ))


@api.handle_get('/authenticate', API_VER)
@requires_authenticated()
async def touch(request: Request) -> JSONResponse:
    session: Session = request.user.session
    await session.touch()
    user: SessionUser = context['user']
    response: ISession = user.session.as_json()
    return JSONResponse(response)


@api.handle_delete('/authenticate', API_VER)
@requires_authenticated()
async def logoff(request: Request) -> NoContentResponse:
    session: Session = request.user.session
    await session.drop()
    return NoContentResponse()


@api.handle_put('/authenticate', API_VER)
async def refresh(request: Request) -> JSONResponse:
    payload = request.scope['payload']
    given_token: str = payload['token']

    token: str
    refresh_token: str
    expire: datetime.datetime
    user: User
    user, token, refresh_token, expire = await refresh_with_token(given_token)

    return JSONResponse(await _auth_response(
        user, token, refresh_token, expire
    ))
