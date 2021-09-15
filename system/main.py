from typing import *
import os
import asyncio
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import config
from . import apps, ds, requests, settings, l10n, middlewares, logger, ui, runtime


# Ensures the environment
os.makedirs(config.ASSETS_ROOT, exist_ok=True)
os.makedirs(config.STATICS_ROOT, exist_ok=True)

# Collecting the list of loading apps. The first one is core 'system' app.
apps_to_load: List[str] = [config.COREDIR]
apps_to_load.extend(config.APPS_ENABLED)

# Actually loading each app in the order they been declared in the config.
project_apps: apps.IAppsModules = apps.load(apps_to_load)

# Initalizing apps' main modules
apps_main: apps.IAppsMains = apps.initialize(project_apps)


def get_default_path() -> str:
    """ Returns an URL where to redirect the client browser when accesing
    the root (/) path.
    """
    is_authenticated: bool = runtime.context['is_authenticated']
    default_url: str = \
        (
            getattr(config, 'DEFAULT_URL_AUTHENTICATED', None)
            if is_authenticated
            else getattr(config, 'DEFAULT_URL_GUEST', None)
        ) or config.DEFAULT_URL
    return default_url


async def default_route(request: requests.Request) -> requests.Response:
    """ Handles the route when none of the upper corresponds to. Handles
    cases when the user tryes to access the non-existence path, the
    or static file (useful for development environment).
    """
    rop: str = request.path_params['rest_of_path'].replace('..', '')
    if requests.is_static_path(rop):
        return requests.PrebuiltFile(rop)

    return requests.RedirectResponse(get_default_path(), 307)


async def root_route(*_) -> requests.RedirectResponse:
    """ Handles the exactly root route (/). """
    return requests.RedirectResponse(get_default_path(), 307)


async def start():
    """ The main entry point where async process begins to work. """

    for _main in apps_main.values():
        # For the every app, if there is a 'start' function in the
        # it's 'app.py' module - do execute this function.
        if not hasattr(_main, 'start'):
            continue
        _start: Any = getattr(_main, 'start')
        if not callable(_start):
            continue
        (await _start()) if asyncio.iscoroutinefunction(_start) else _start()


# The place where ASGI about to be prepared to start

_middlewares: List[Middleware] = [
    Middleware(requests.middleware.RequestMiddleware),
    Middleware(requests.middleware.ContextMiddleware),
    Middleware(ds.middleware.RedisConnectionMiddleware),
    Middleware(ds.middleware.DatastorageConnectionMiddleware),
    Middleware(settings.middleware.SettingsMiddleware),
    Middleware(l10n.middleware.LocalizationMiddleware),
]
_middlewares.extend(middlewares.registered)


logger.debug(
    "middlewares in use (ordered):\n" + '\n'.join([str(m) for m in _middlewares])
)


_routes: List[Union[Route, Mount]] = requests.routing.registered
_routes.insert(0, requests.Route('/', root_route, methods=['GET']))
_routes.append(Route(config.AUTH.get('login_screen_url', '/login'), ui.screens.Screen.endpoint, methods=['GET']))
_routes.append(Mount(config.STATICS_URL, app=StaticFiles(directory=config.STATICS_ROOT), name='static'))
_routes.append(requests.Route('/{rest_of_path:path}', default_route, methods=['GET']))


# Creating the ASGI actual instance
asgi = Starlette(
    on_startup=[start],
    middleware=_middlewares,
    routes=_routes,
    debug=False
)

