"""
Provides ASGI/routing-level wrappers for the authentication mechanics used by the project and
by the middleware.
"""

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
    """ Raises the specific for situation exception if the current, logged-in user has
    no access to the requesting facility. On other side, if the user HAS the access,
    nothing will happen.
    The testing is connection-level, so, the `HTTPConnection` about to be passed to
    this function.

    If the user is not logged-in, but requested to be - the 401 status code (Not
    authenticated) will be used as exception; otherwise, 403 (Access denied)
    will be returned if even one scope is not accessible by the user.

    :param conn:
        The ASGI connection for which context to test the access;
    :param scopes:
        The requested scoped to be accessible by the current (based on the connection
        session) user;
    :param status_code:
        Which status code to raise if the user has no access (but IS logged-in);
    :param redirect:
        Instead of raising "Access denied" or "Not authenticated" exception - redirect
        the calling client to the given URL; optional argument;
    """

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
    """ The decorator used to protect the decorating function, controller,
    method or etc., with specified by the application set of permissions
    (scopes). If the current user has no access to any of the specified
    permissions when the decorated function apear to be run - the
    corresponding exception will be raised, preventing client from doing
    unaccessible work.

    Example:

    .. highlight:: python
    .. code-block:: python

        # Require 'extra_access' named permission to be present in the
        # any of role which the current user is belongs to.
        @requires('extra_access')
        async def my_controller(request: Request) -> Response:
            pass

    :param scopes:
        The list of scopes (permissions) required to be accessible for
        the current user;
    :param status_code:
        Which status code to use (403 by default) if the user is logged-in,
        but has no access to the any of the specified scopes;
    :param redirect:
        Instead of raising "Access denied" or "Not authenticated" exception - redirect
        the calling client to the given URL; optional argument;
    """

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
    """ The shortcut decoractor for the `requires('authenticated')` """

    return requires('authenticated', status_code=status_code, redirect=redirect)


def requires_guest(
    status_code: int = 403,
    redirect: str = None,
) -> Callable:
    """ The shortcut decoractor for the `requires('guest')` """

    return requires('guest', status_code=status_code, redirect=redirect)
