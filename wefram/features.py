"""
Provides the platform `features` functionality.

Adds the ability to register features whose one or the another application provides.
The one application may register one or several features, giving other applications an
ability to "known" that some feature is available.

For example, the application which make possible to send messages to the Telegram chat,
registers the feature, let's say, named "telegram-sending".
The other application, for example - some monitoring service, relies on whose notification
channels are available. And, for example, depending on that is the corresponding
feature registered (say, is the "telegram-sending" feature registered) - this application
allows the user to select or not the Telegram channel for notifications.

Accordingly, if the application, whise provides the one or the another feature, will be
disabled or even deinstalled - its features will not be registered and other applications,
whose relies on those features, may handle this situation.
"""

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
    """ Registers the feature for the application. By default the calling app name
    will be used as the feature parent. This may be overriding by setting the ``app``
    argument to the other that calling app.
    """

    app = app or get_calling_app()
    registered.setdefault(app, set()).add(name)
    logger.debug(f"registered feature {CSTYLE['green']}{app}.{name}{CSTYLE['clear']}")


def has(fqname: str) -> bool:
    """ Returns ``True`` if the given feature is registered. If the only app name given
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
    standard feature fqname: ``<app>.<feature>``.
    """

    features: List[str] = []
    for app, names in registered.items():
        if not registered[app]:
            continue
        [features.append('.'.join([app, name])) for name in names]
    [features.append(app) for app in apps.get_apps_loaded()]
    return features

