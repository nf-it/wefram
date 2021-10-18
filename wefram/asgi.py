from typing import *
import asyncio
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from . import run, config, requests, logger, ds, runtime, middlewares, ui


def get_default_path() -> str:
    """ Returns an URL where to redirect the client browser when accesing the root (/) path. """

    is_authenticated: bool = runtime.context['is_authenticated']
    return (
        config.URL['default_authenticated'] if is_authenticated else config.URL['default_guest']
    ) or config.URL['default']


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

    for _main in run.apps_main.values():
        # For the every app, if there is a 'start' function in the
        # it's 'app.py' module - do execute this function.
        if not hasattr(_main, 'start'):
            continue
        _start: Any = getattr(_main, 'start')
        if not callable(_start):
            continue
        (await _start()) if asyncio.iscoroutinefunction(_start) else _start()

    await ds.history.start()


# The place where ASGI about to be prepared to start

logger.debug(
    "middlewares in use (ordered):\n" + '\n'.join(["  %s" % str(m) for m in middlewares.registered])
)


_routes: List[Union[Route, Mount]] = requests.routing.registered
_routes.insert(0, requests.Route('/', root_route, methods=['GET']))
_routes.append(Route(config.URL['login_screen'], ui.screens.Screen.endpoint, methods=['GET']))
_routes.append(Mount(config.STATICS_URL, app=StaticFiles(directory=config.STATICS_ROOT), name='static'))
_routes.append(requests.Route('/{rest_of_path:path}', default_route, methods=['GET']))


# Creating the ASGI actual instance
asgi = Starlette(
    on_startup=[start],
    middleware=middlewares.registered,
    routes=_routes,
    debug=False
)

