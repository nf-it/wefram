from typing import *
from starlette.middleware import Middleware


__all__ = [
    'Middleware',
    'registered',
    'register',
]


registered: List[Middleware] = []


def register(middleware: Middleware) -> None:
    if not isinstance(middleware, Middleware):
        raise TypeError(f"middleware must be registered as Middleware object, {type(middleware)} given instead")
    registered.append(middleware)

