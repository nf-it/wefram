from typing import *
from starlette.routing import Route
from ..requests import routing


__all__ = [
    'handle_req',
    'handle_get',
    'handle_post',
    'handle_put',
    'handle_delete',
    'handle_patch',
    'handle_head',
    'handle_options'
]


def _rq(endpoint: Callable, path: str, method: Union[str, List[str]], version: Optional[Union[int, str]] = None) -> Callable:
    """
    API route path format:
    /api/{app_name}/v1/{path} -- for versioned route ('version' argument is not omitted)
    /api/{app_name}/{path} -- for non-versioned route
    """
    methods: List[str] = [method] if isinstance(method, str) else list(method)
    path_ver: str = '' if not version else f"/v{version}"
    route_path: str = routing.format_path(path, 'api', path_ver)
    routing.append(Route(route_path, endpoint, methods=methods))
    return endpoint


def handle_req(
        path: str,
        version: Optional[Union[int, str]] = None,
        methods: Optional[Union[str, List[str]]] = 'GET'
) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, methods, version)
    return decorator


def handle_get(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'GET', version)
    return decorator


def handle_post(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'POST', version)
    return decorator


def handle_put(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'PUT', version)
    return decorator


def handle_delete(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'DELETE', version)
    return decorator


def handle_patch(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'PATCH', version)
    return decorator


def handle_head(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'HEAD', version)
    return decorator


def handle_options(path: str, version: Optional[Union[int, str]] = None) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        return _rq(endpoint, path, 'OPTIONS', version)
    return decorator
