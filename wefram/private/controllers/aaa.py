from typing import *
import datetime
from asyncio import sleep
from ... import api, logger, settings
from ...requests import Request, NoContentResponse, JSONResponse, HTTPException
from ...runtime import context
from ...exceptions import AuthenticationFailed
from ...aaa.wrappers import requires_authenticated
from ...aaa.routines import authenticate, create_session, refresh_with_token
from ...models import User, Session, SessionLog, SessionUser
from ..const.aaa import SETTINGS_FAILEDAUTH_DELAY, SETTINGS_SUCCEEDAUTH_DELAY


API_V1: int = 1


async def _auth_response(
        user: User,
        token: str,
        refresh_token: str,
        expire: datetime.datetime
) -> dict:
    return {
        'token': token,
        'refreshToken': refresh_token,
        'user': user.json(set_name='session'),
        'expire': expire.isoformat(timespec='seconds'),
        'permissions': await user.all_permissions()
    }


@api.handle_get('/check', API_V1)
@requires_authenticated()
async def v1_check(request: Request) -> NoContentResponse:
    return NoContentResponse()


@api.handle_post('/authenticate', API_V1)
async def v1_login(request: Request) -> JSONResponse:
    payload: Dict[str, str] = request.scope['payload']
    username: str = payload.get('username', None)
    password: str = payload.get('password', None)

    if not username or not password:
        logger.debug("no username or password", 'login')
        raise HTTPException(400)

    try:
        user: User = await authenticate(username, password)
    except AuthenticationFailed:
        logger.info(f"authentication failed for '{username}'", 'login')
        await sleep((await settings.get('aaa'))[SETTINGS_FAILEDAUTH_DELAY] * 1.0)
        raise HTTPException(401)

    token: str
    refresh_token: str
    expire: datetime.datetime
    token, refresh_token, expire = await create_session(user)
    logger.info(f"successfully authenticated '{username}'", 'login')

    await sleep((await settings.get('aaa'))[SETTINGS_SUCCEEDAUTH_DELAY] * 1.0)

    await SessionLog.create(
        user_id=user.id,
        ts=datetime.datetime.now(),
        extra={
            'from': request.client.host,
            'host': request.headers.get('host', None),
            'user_agent': request.headers.get('user-agent', None)
        }
    )

    return JSONResponse(await _auth_response(
        user, token, refresh_token, expire
    ))


@api.handle_get('/authenticate', API_V1)
@requires_authenticated()
async def v1_touch(request: Request) -> JSONResponse:
    session: Session = request.user.session
    await session.touch()
    user: SessionUser = context['user']
    response: dict = user.session.as_json()
    return JSONResponse(response)


@api.handle_delete('/authenticate', API_V1)
@requires_authenticated()
async def v1_logoff(request: Request) -> NoContentResponse:
    session: Session = request.user.session
    await session.drop()
    return NoContentResponse()


@api.handle_put('/authenticate', API_V1)
async def v1_refresh(request: Request) -> JSONResponse:
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
