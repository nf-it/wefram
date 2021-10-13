from typing import *
from inspect import isclass
from starlette.middleware import Middleware
from .cli import CliMiddleware
from .private import middlewares
from . import config


__all__ = [
    'Middleware',
    'registered',
    'registered_cli',
    'start',
    'register',
    'register_for_cli'
]


registered: List[Middleware] = [
    Middleware(middlewares.RequestMiddleware),
    Middleware(middlewares.ContextMiddleware),
    Middleware(middlewares.RedisConnectionMiddleware),
    Middleware(middlewares.DatastorageConnectionMiddleware),
    Middleware(middlewares.SettingsMiddleware),
    Middleware(middlewares.LocalizationMiddleware),
    Middleware(
        middlewares.AuthenticationMiddleware,
        backend=middlewares.ProjectAuthenticationBackend(
            secret=config.AUTH['secret'],
            audience=config.AUTH['audience'],
            schema='Bearer',
            algorithm='HS256'
        )
    ),
]
registered_cli: List = [
    middlewares.DatastorageConnectionCliMiddleware,
    middlewares.RedisConnectionCliMiddleware,
    middlewares.AuthenticationCliMiddleware,
    middlewares.LocalizationCliMiddleware,
    middlewares.SettingsCliMiddleware
]


def start() -> None:
    pass


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
