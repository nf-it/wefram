from typing import *
import inspect
import asyncio
import functools
from starlette.requests import HTTPConnection, Request
from starlette.authentication import UnauthenticatedUser
from starlette.websockets import WebSocket
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from ..tools import get_calling_app


__all__ = [
    'requires',
    'requires_authenticated',
    'requires_guest',
    'AUTHENTICATED',
    'GUEST'
]


AUTHENTICATED: str = 'authenticated'
GUEST: str = 'guest'


def test_request_scope(
        conn: HTTPConnection,
        scopes: Sequence[str],
        status_code: int = 403,
        redirect: str = None
) -> Optional[str]:
    if scopes and scopes[0].lower() == 'guest' and not isinstance(conn.user, UnauthenticatedUser) and conn.user is not None:
        if redirect is not None:
            return redirect
        raise HTTPException(403)
    if scopes and scopes[0].lower() == 'guest':
        return
    if isinstance(conn.user, UnauthenticatedUser) or conn.user is None:
        if redirect is not None:
            return redirect
        raise HTTPException(401)
    for scope in scopes:
        if scope in conn.auth.scopes:
            continue
        raise HTTPException(status_code)


def requires(
    scopes: Union[str, Sequence[str]],
    status_code: int = 403,
    redirect: str = None
) -> Callable:
    def _ensure_app_prefix(scope: str) -> str:
        if scope in ['authenticated', 'guest']:
            return scope
        if '.' in scope:
            return scope
        return f"{app}.{scope}"

    app: str = get_calling_app()
    scopes_list = [
        _ensure_app_prefix(scope)
        for scope in ([scopes] if isinstance(scopes, str) else list(scopes))
    ]

    def decorator(func: Callable) -> Callable:
        # This part of code is just a copy from upper 'requires' Starlette default
        # decorator.
        rtype: Optional[str]
        sig = inspect.signature(func)
        is_method: bool = False
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == 'self' or parameter.name == 'cls':
                is_method = True
            if parameter.name != "request" and parameter.name != "websocket":
                continue
            rtype = parameter.name
            break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if is_method:
            idx -= 1

        # For the websocket we cannot return different answers: 401 for unauthenticated and
        # 403 for authenticated, but not permitted user. But we can test for 'guest'
        # scope.
        if rtype == 'websocket':
            @functools.wraps(func)
            async def ws_wrapper(*args, **kwargs):
                # Testing against authenticated/non-authenticated websocket connection
                websocket = kwargs.get("websocket", args[idx] if args else None)
                assert isinstance(websocket, WebSocket)
                try:
                    test_request_scope(websocket, scopes_list)
                except HTTPException:
                    await websocket.close()
                    return

                # Calling upper Starlette's 'requires'-decorated default mechanics
                await func(*args, **kwargs)
            return ws_wrapper

        elif asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)
                r: Optional[str] = test_request_scope(request, scopes_list, status_code, redirect)
                if r:
                    return RedirectResponse(
                        url=request.url_for(r), status_code=303
                    )

                # Calling upper Starlette's 'requires'-decorated default mechanics
                return await func(*args, **kwargs)
            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)
                r: Optional[str] = test_request_scope(request, scopes_list, status_code, redirect)
                if r:
                    return RedirectResponse(
                        url=request.url_for(r), status_code=303
                    )

                # Calling upper Starlette's 'requires'-decorated default mechanics
                return func(*args, **kwargs)
            return sync_wrapper

    return decorator


def requires_authenticated(
    status_code: int = 403,
    redirect: str = None,
) -> Callable:
    return requires('authenticated', status_code=status_code, redirect=redirect)


def requires_guest(
    status_code: int = 403,
    redirect: str = None,
) -> Callable:
    return requires('guest', status_code=status_code, redirect=redirect)
