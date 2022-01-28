"""
Provides different authentication and authorization functionality which is out of models' API.
"""

from typing import *
import datetime
from asyncio import sleep
from ... import api, logger, settings
from ...requests import Request, NoContentResponse, JSONResponse, HTTPException, SuccessResponse
from ...runtime import context
from ...exceptions import AuthenticationFailed
from ...aaa.wrappers import requires_authenticated, requires
from ...aaa.routines import authenticate, create_session, refresh_with_token, drop_user_sessions_by_id
from ...models import User, Session, SessionLog, SessionUser
from ..const.aaa import SETTINGS_FAILEDAUTH_DELAY, SETTINGS_SUCCEEDAUTH_DELAY, PERMISSION_ADMINUSERSROLES


API_V1: int = 1


async def _auth_session_state_response(
        user: User,
        token: str,
        refresh_token: str,
        expire: datetime.datetime
) -> dict:
    """ Prepares the JSON response with the new JWT token, ready to response. """

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
    """ The only reason for this controller is to give an ability the frontend
    to test is the current user logged in or have been logged off by the backend
    due to the session expire (for example). This controller does not touchs
    the session (not updates the last activity timestamp of the user).

    Returns 204 if the user's session is still valid, 401 otherwise.
    """

    return NoContentResponse()


@api.handle_post('/authenticate', API_V1)
async def v1_login(request: Request) -> JSONResponse:
    """ Authenticates the user by given login and password pair. The request
    awaits to be a json:

    {
        "username": "<login>",
        "password": "<plain text password>"
    }

    If the given pair is valid - the new session for the found by "login" user
    will be created, the new session's JWT token will be generated and returned
    to the calling frontend.

    Returns the new session state.
    """

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

    return JSONResponse(await _auth_session_state_response(
        user, token, refresh_token, expire
    ))


@api.handle_get('/authenticate', API_V1)
@requires_authenticated()
async def v1_touch(request: Request) -> JSONResponse:
    """ Refreshes the user session, preventing from log off by expiration time.
    The controller acts with the current session by the given request header context,
    so it is not applicable to the not logged in clients.

    Returns the current user's data as JSON response
    (see :class:~wefram.models.aaa.Session: method *as_json* for more details)
    """

    session: Session = request.user.session
    await session.touch()
    user: SessionUser = context['user']  # why to get the user and then its session?? see upper??
    response: dict = user.session.as_json()
    return JSONResponse(response)


@api.handle_delete('/authenticate', API_V1)
@requires_authenticated()
async def v1_logoff(request: Request) -> SuccessResponse:
    """ Logs off the current user's session. The controller acts with the
    current session by the given request header context, so it is not
    applicable to the not logged in clients.

    Returns 204 response
    """

    session: Session = request.user.session
    await session.drop()
    return SuccessResponse()


@api.handle_put('/authenticate', API_V1)
async def v1_refresh(request: Request) -> JSONResponse:
    """ Refreshed the current user's session's JWT token by generating
    the new one. The controller acts with the current session by the
    given request header context, so it is not applicable to the not
    logged in clients.

    Returns new session state with the new JWT in it.
    """

    payload = request.scope['payload']
    given_token: str = payload['token']

    token: str
    refresh_token: str
    expire: datetime.datetime
    user: User
    user, token, refresh_token, expire = await refresh_with_token(given_token)

    return JSONResponse(await _auth_session_state_response(
        user, token, refresh_token, expire
    ))


@api.handle_post('/users/lock', API_V1)
@requires(PERMISSION_ADMINUSERSROLES)
async def v1_lock_users(request: Request) -> SuccessResponse:
    """ Locks given system users by their 'id' field preventing from loggin in.

    Request's payload must consist of JSON:

    {
        "ids": [
            "<user.id>",
            "<user.id>",
            ...
        ]
    }

    Returns 204 response
    """

    payload = request.scope['payload']
    ids: Optional[List[str]] = payload.get('ids')
    if not ids:
        raise HTTPException(500, "Invalid request - 'ids' payload was not specified!")
    if not isinstance(ids, (list, tuple)):
        raise HTTPException(500, "Invalid request - 'ids' must be a list of users' id!")

    await User.update_locked_state(True, ids)

    return SuccessResponse()


@api.handle_post('/users/unlock', API_V1)
@requires(PERMISSION_ADMINUSERSROLES)
async def v1_unlock_users(request: Request) -> SuccessResponse:
    """ Unlocks given system users by their 'id' field preventing from loggin in.
    Request's payload must consist of JSON:

    {
        "ids": [
            "<user.id>",
            "<user.id>",
            ...
        ]
    }

    Returns 204 response
    """

    payload = request.scope['payload']
    ids: Optional[List[str]] = payload.get('ids')
    if not ids:
        raise HTTPException(500, "Invalid request - 'ids' payload was not specified!")
    if not isinstance(ids, (list, tuple)):
        raise HTTPException(500, "Invalid request - 'ids' must be a list of users' id!")

    await User.update_locked_state(False, ids)

    return SuccessResponse()


@api.handle_post('/users/logoff', API_V1)
@requires(PERMISSION_ADMINUSERSROLES)
async def v1_logoff_users(request: Request) -> SuccessResponse:
    """ Logs off all given users, terminating all their corresponding sessions.
    The list of users must be given by their 'ids'.

    Request's payload must consist of JSON:

    {
        "ids": [
            "<user.id>",
            "<user.id>",
            ...
        ]
    }

    Returns 204 response
    """

    payload = request.scope['payload']
    user_ids: Optional[List[str]] = payload.get('ids')
    if not user_ids:
        raise HTTPException(500, "Invalid request - 'ids' payload was not specified!")
    if not isinstance(user_ids, (list, tuple)):
        raise HTTPException(500, "Invalid request - 'ids' must be a list of users' id!")

    for user_id in user_ids:
        if not isinstance(user_id, str):
            raise HTTPException(500, "Invalid request - 'ids' must be a list of users' id!")
        await drop_user_sessions_by_id(user_id)

    return SuccessResponse()

