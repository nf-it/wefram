import inspect
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
    """ The wrapper class extending the Starlette's Route class """

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
        """ Decorating the endpoint (if the endpoint is a function or method) with
        extra functionality. """

        if inspect.isclass(endpoint):
            # If the endpoint is the HTTPEndpoint class - return is
            # straight without any decoration
            return endpoint

        # Decorate the endpoint function with some extra functionality
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
    """ Appends the given route to the routing table of the project."""

    _methods: str = ','.join(str(s) for s in r.methods)
    logger.debug(f"routed {CSTYLE['white']}{_methods}{CSTYLE['clear']} {CSTYLE['pink']}{r.path}{CSTYLE['clear']}")
    registered.append(r)


def abs_url(path: str, app: Optional[str] = None) -> str:
    """ Returns the absolete URL for the given path and app. If the app
    has been ommited - use the calling app by default. """

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
    """ Decorator used to route the function endpoint. It appends the resulting
    route to the routing table of the project. """

    def decorator(endpoint: Callable) -> Callable:
        request_methods = methods or ['GET']
        append(Route(format_path(path), endpoint, methods=request_methods))
        return endpoint
    return decorator


def is_static_path(p: str) -> bool:
    """ Returns `True` if the given FQ path is the static one (endpoints to
    the static file storage, not the response function or class), and `False`
    otherwise. """

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

