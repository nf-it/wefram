from typing import *
from types import ModuleType
import asyncio
import os
import os.path
import importlib

from .. import config, tools, logger, apps
from ..tools import CSTYLE


TARGETS = {
    'all': "Make everything",
    'assets': "Make assets only, without frontend compiling",
    'cleanall': "Remove all made builds",
    'db': "Make database (PostgreSQL) migrations",
    'depends': "Install project dependencies, both backend & frontend",
    'front': "Make frontend: assets, screens, react",
    'l10n': "Collect and build localizations",
    'pip': "Install project backend dependencies",
    'react': "Compile frontend using webpack (only), not making screens & others",
    'screens': "Prepare frontend screens to be compiled with react",
    'setup': "Re-install project with cleaning all data and making everything",
    'setup demo': "Run `setup` terget and upload demo data after",
    'texts': "Collect and build static texts",
    'webpack': "Prepare required webpack configuration and install node dependencies"
}


def print_help() -> None:
    print("")
    print(f"Available targets for {CSTYLE['yellow']}make{CSTYLE['clear']}:")
    print("")
    for k in sorted(TARGETS.keys()):
        print(f"{CSTYLE['red']}{k}{CSTYLE['clear']}")
        print("  ", TARGETS[k])
    print("")


async def run(targets: list) -> None:
    if not targets:
        targets = ['all']

    if targets[0] == 'help':
        print_help()
        return

    logger.set_level(max(logger.VERBOSITY, logger.INFO))
    logger.info(f"starting to make the project", 'make')

    # Initially loading the project
    importlib.import_module('.'.join([config.COREPKG, 'run']))

    # The list of apps to build
    apps_to_build: List[str] = apps.get_apps_loaded()

    # The list of project roots whose about to make
    roots: List[str] = []
    if config.ASSETS_DIR:
        roots.append(config.ASSETS_DIR)

    # Defining the global build context which may be used by apps
    ctx: dict = dict()
    ctx['apps']: List[str] = apps_to_build
    ctx['apps_build']: Dict[str, ModuleType] = dict()

    # The apps' specific build logic
    makes: List[Tuple[str, callable]] = []

    for name in apps_to_build:
        root: str = tools.app_root(name)
        if not os.path.isdir(root):
            raise FileNotFoundError(
                f"app '{name}' has not been found (is not installed, but is enabled?)"
            )

        roots.append(name)

        if name == config.COREPKG or name == 'wefram' or name == 'system':
            continue

        app_module: ModuleType = apps.modules[name]
        if not hasattr(app_module, 'build'):
            continue
        app_build: Any = getattr(app_module, 'build')
        if not isinstance(app_module, ModuleType):
            raise TypeError(
                f"'{name}'.build must be module, got the '{type(app_build)}' instead!"
            )
        makefunc: callable = getattr(app_build, 'make', None)
        if makefunc is None:
            continue
        if not callable(makefunc):
            raise TypeError(
                f"{name}.build.make is not an async callable coroutine"
            )
        makes.append((name, makefunc))
        ctx['apps_build'][name] = app_build

    for makefunc in makes:
        name: str
        func: callable
        name, func = makefunc
        logger.info(f"Build {CSTYLE['bold']}{name}{CSTYLE['clear']}")
        await func(ctx)

    # Executing specified make targets
    for target in targets:
        logger.info(f"making the target: {CSTYLE['bold']}{target}{CSTYLE['clear']}", 'make')
        try:
            target_module: ModuleType = importlib.import_module('.'.join([config.COREPKG, 'manage', 'targets', target]))

        except ModuleNotFoundError as exc:
            raise RuntimeError(
                f"Cannot find facility serves the make target '{target}'!"
            ) from exc

        makefunc: callable = getattr(target_module, 'run')
        if asyncio.iscoroutinefunction(makefunc):
            await makefunc(roots)
        else:
            makefunc(roots)

