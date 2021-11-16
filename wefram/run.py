from typing import *
import os

from . import config, apps, requests, logger, ds, runtime, middlewares, ui, l10n
from .private import (
    controllers as private_controllers,
    api as private_apis,
    screens as private_screens
)


apps.start()
requests.start()
logger.start()
ds.start()
runtime.start()
middlewares.start()
ui.start()
l10n.start()

private_controllers.start()
private_apis.start()
private_screens.start()


# Ensures the environment
os.makedirs(config.BUILD_ROOT, exist_ok=True)
os.makedirs(config.ASSETS_ROOT, exist_ok=True)
os.makedirs(config.STATICS_ROOT, exist_ok=True)

# Collecting the list of loading apps. The first one is core 'system' app.
apps_to_load: List[str] = ['system']
apps_to_load.extend(config.APPS_ENABLED)

# Actually loading each app in the order they been declared in the config.
project_apps: apps.IAppsModules = apps.load(apps_to_load)

# Initalizing apps' main modules
apps_main: apps.IAppsMains = apps.initialize(project_apps)


def start() -> None:
    pass


def ensure_started() -> None:
    pass
