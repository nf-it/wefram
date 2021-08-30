from typing import *
import types
import importlib
import config
from .l10n import L10nStr
from .tools import CSTYLE, app_path, app_has_module
from . import logger


__all__ = [
    'IAppsModules',
    'IAppsMains',
    'modules',
    'mains',
    'has',
    'is_enabled',
    'load',
    'initialize',
    'get_app_caption',
    'get_apps_loaded',
    'get_apps_sorted'
]


IAppsModules = Dict[str, types.ModuleType]
IAppsMains = Dict[str, types.ModuleType]


modules: IAppsModules = {}
mains: IAppsMains = {}


def has(app: str) -> bool:
    return app in modules


def is_enabled(app: str) -> bool:
    return app in config.APPS_ENABLED or app in modules


def load(apps: List[str]) -> Dict[str, types.ModuleType]:
    """ The first stage of apps loading. Importing apps' package modules. """

    for name in apps:
        logger.info(
            f"loading app {CSTYLE['green']}{name}{CSTYLE['clear']}"
        )
        path: str = app_path(name)
        module: types.ModuleType = importlib.import_module(path)
        modules[name] = module
    return modules


def initialize(apps: Dict[str, types.ModuleType]) -> Dict[str, types.ModuleType]:
    """ The second stage of apps loading. Trying to import apps' package's
    modules called 'app.py', if present.
    """
    for name, package in apps.items():
        if not app_has_module(package, 'app'):
            continue
        logger.info(
            f"initializing app {CSTYLE['green']}{name}{CSTYLE['clear']} [app.py]"
        )
        path: str = app_path(name)
        main: types.ModuleType = importlib.import_module('.'.join([path, 'app']))
        mains[name] = main
    return mains


def get_apps_loaded() -> List[str]:
    """ Returns a list of all loaded (enabled) apps in the project. """
    return list(modules.keys())


def get_app_caption(app_name: str) -> Union[str, L10nStr]:
    """ Returns the app's caption, or the app's name if there is no
    caption defined by CAPTION const in the [app.py].
    """
    if app_name not in modules:
        raise KeyError(f"app '{app_name}' has not been found")
    if app_name not in mains:
        return app_name
    return getattr(mains[app_name], 'CAPTION', app_name)


def get_apps_sorted() -> List[str]:
    """ Returns a list of apps' names sorted by the ORDER [app.py] and
    then by the apps' captions.
    """
    orders: Dict[str, int] = {}
    loaded: List[str] = get_apps_loaded()
    for name in loaded:
        if name not in mains:
            continue
        order: Optional[int] = getattr(mains[name], 'ORDER', None)
        if order is None:
            continue
        orders[name] = int(order)

    default_order: int = max(orders.values()) + 10 if orders else 10
    return sorted(
        [name for name in loaded if name != 'system'],
        key=lambda n: (orders.get(n, default_order), get_app_caption(n))
    ) + ['system']


def get_apps_order() -> Dict[str, int]:
    """ Returns a dict containing the apps' names as keys and their
    corresponding order (number) as values.
    """

    orders: Dict[str, int] = {}
    loaded: List[str] = get_apps_loaded()
    for name in loaded:
        if name not in mains:
            continue
        order: Optional[int] = getattr(mains[name], 'ORDER', None)
        if order is None:
            continue
        orders[name] = int(order)

    default_order: int = max(orders.values()) + 10 if orders else 10
    last_order: int = default_order + 99999
    orders['system'] = last_order

    return {
        name: orders.get(name, default_order) for name in loaded
    }
