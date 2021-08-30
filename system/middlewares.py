from typing import *
from inspect import isclass
from starlette.middleware import Middleware
from .cli import CliMiddleware


__all__ = [
    'Middleware',
    'registered',
    'registered_cli',
    'register',
    'register_for_cli'
]


registered: List[Middleware] = []
registered_cli: List = []


def register(cls: ClassVar, **options) -> ClassVar:
    """ Decorator registering the request middleware in the system """

    middleware: Middleware = Middleware(cls, **options)
    registered.append(middleware)
    return middleware


def register_for_cli(cls: ClassVar[CliMiddleware]) -> ClassVar:
    """ Decorator registering the special CLI middleware in the system """

    if not isclass(cls) or not issubclass(cls, CliMiddleware):
        raise TypeError(f"CLI middleware must be registered as CliMiddleware-based class, {type(cls)} given instead")
    registered_cli.append(cls)
    return cls
