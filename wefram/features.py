from typing import *
from .tools import CSTYLE, get_calling_app
from . import logger, apps


__all__ = [
    'registered',
    'register',
    'has',
    'all_features'
]


registered: Dict[str, Set[str]] = {}


def register(name: str, app: Optional[str] = None) -> None:
    app = app or get_calling_app()
    registered.setdefault(app, set()).add(name)
    logger.debug(f"registered feature {CSTYLE['green']}{app}.{name}{CSTYLE['clear']}")


def has(fqname: str) -> bool:
    """ Returns True if the given feature is registered. If the only app name given
    in the argument (no dot in the name specified) - than just returns the existance
    of the given app in the enabled apps.
    """
    if '.' not in fqname:
        # If there is no dot in the fqname - returning the existance of the app generally
        return apps.is_enabled(fqname)

    app: str
    name: str
    app, name = fqname.split('.', 1)
    if app not in registered:
        return False

    return name in registered[app]


def all_features() -> List[str]:
    """ Returns a straight list of all features registered, formatting as
    standard feature fqname: <app>.<feature>
    """

    features: List[str] = []
    for app, names in registered.items():
        if not registered[app]:
            continue
        [features.append('.'.join([app, name])) for name in names]
    [features.append(app) for app in apps.get_apps_loaded()]
    return features

