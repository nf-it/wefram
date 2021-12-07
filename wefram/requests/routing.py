from typing import *
from starlette.routing import Route as _Route, Request, PlainTextResponse
from starlette.responses import Response
from ..tools import CSTYLE, get_calling_app
from .. import logger, exceptions


__all__ = [
    'Route',
    'registered',
    'route',
    'append',
    'abs_url',
    'format_path',
    'static_routes_prefixes',
    'is_static_path'
]


class Route(_Route):
    def __init__(
            self,
            path: str,
            endpoint: Callable,
            *,
            methods: List[str] = None,
            name: str = None,
            **kwargs
    ):
        super().__init__(
            path,
            self._decorate_endpoint(endpoint),
            methods=methods,
            name=name,
            **kwargs
        )

    def _decorate_endpoint(self, endpoint: Callable) -> Callable:
        async def _decorated(request: Request) -> Response:
            try:
                return await endpoint(request)

            except exceptions.AccessDenied:
                return PlainTextResponse("Forbidden", status_code=403)

            except exceptions.NotAuthenticated:
                return PlainTextResponse("Unauthorized", status_code=401)

            except exceptions.ObjectNotFoundError as e:
                return PlainTextResponse(e.details, status_code=404)

            except exceptions.ApiError as e:
                return PlainTextResponse(e.details, status_code=e.status_code)

            except exceptions.DatabaseError as e:
                return PlainTextResponse(e.details, status_code=e.status_code)

        return _decorated


registered: List[Route] = []
static_routes_prefixes: List[str] = [
    '/static'
]


def append(r: Route) -> None:
    _methods: str = ','.join(str(s) for s in r.methods)
    logger.debug(f"routed {CSTYLE['white']}{_methods}{CSTYLE['clear']} {CSTYLE['pink']}{r.path}{CSTYLE['clear']}")
    registered.append(r)


def abs_url(path: str, app: Optional[str] = None) -> str:
    app = app or get_calling_app()
    if path.startswith('//'):
        return path[1:]
    if path == '/':
        path = ''
    return '/' + ('/'.join([s for s in (app, path.lstrip('/')) if s])).lstrip('/')


def format_path(
        relpath: str,
        prefix: Optional[str] = None,
        inner: Optional[str] = None,
        suffix: Optional[str] = None
) -> str:
    if relpath.startswith('//'):
        return relpath[1:]
    route_app: str = get_calling_app()
    prefix: str = '' if not prefix else prefix.strip('/')
    inner: str = '' if not inner else inner.strip('/')
    suffix: str = '' if not suffix else suffix.strip('/')
    return f"/{'/'.join([s for s in [prefix, route_app, inner, relpath.strip('/'), suffix] if s])}".\
        rstrip('/').replace('//', '/')


def route(path: str, methods: Optional[List[str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        request_methods = methods or ['GET']
        append(Route(format_path(path), endpoint, methods=request_methods))
        return endpoint
    return decorator


def is_static_path(p: str) -> bool:
    p: str = p.lstrip('/')
    if '/' in p:
        return False
    p: list = p.split('.')
    if len(p) != 2:
        return False
    if len(p[0]) == 0:
        return False
    if len(p[1]) == 0:
        return False
    return True

