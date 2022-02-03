from typing import *


__all__ = [
    'ensure_apps_loaded',
    'make_deploying_srcs',
]


STATE = {
    'loaded': False
}


def ensure_apps_loaded() -> None:
    """ Ensures that all apps been loaded prior to return from this function.
    This routine does nothing if been executed before even once.
    """

    from ... import run

    if STATE['loaded']:
        return

    run.start()
    STATE['loaded'] = True


def make_deploying_srcs() -> List[str]:
    """ Generates the list of rooted files and directories whose about to be
    recursively copied from the development environment to the deployement
    directory.

    Note that only enabled applications will be included into the resulting
    list of deploying sources.

    :return:
        The list of root-level directories and files about to be copied to
        the deployment directory.
    """

    from ... import config

    include_srcs: List[str] = config.DEPLOY.get('include', None) or []
    exclude_srcs: List[str] = config.DEPLOY.get('exclude', None) or []
    sources: List[str] = config.APPS_ENABLED.copy()

    sources.extend([
        'apps.json',
        # 'build.json',   # build.json is not required due to 'deploy.json' usage instead
        # 'config.json',  # the config.json not about to be copied!
        'config.default.json',
        'asgi.py',
        'server.py',
        'requirements.txt'
    ])

    if include_srcs and isinstance(include_srcs, (list, tuple)):
        sources.extend(include_srcs)

    if exclude_srcs and isinstance(exclude_srcs, (list, tuple)):
        sources = [s for s in sources if s not in exclude_srcs]

    return sources

