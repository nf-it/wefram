from typing import *
from types import ModuleType
import os
import re
import shutil
from ..tools import CSTYLE, app_root
from .. import logger, apps
from .locales import Locale
from .catalog import Dictionary
from .config import GENERAL_DICTS_PATH, BUILT_DICTS_PATH
from .const import DEFAULT_APP_DICTS_DIR


def make() -> None:
    shutil.rmtree(BUILT_DICTS_PATH, ignore_errors=True)
    os.makedirs(BUILT_DICTS_PATH, exist_ok=True)
    apps_to_build: apps.IAppsModules = apps.modules
    apps_names: List[str] = list(apps_to_build.keys())

    locales: Dict[str, Locale] = dict()
    dictionaries: Dict[str, Dictionary] = dict()

    source_paths: Dict[str, str] = dict()
    if os.path.isdir(GENERAL_DICTS_PATH):
        source_paths['*'] = GENERAL_DICTS_PATH

    for app_name in apps_names:
        app_build: Optional[ModuleType] = apps_to_build.get(app_name, None)
        dicts_dir: str = \
            getattr(app_build, 'L10N_CATALOG_PATH', DEFAULT_APP_DICTS_DIR) \
            if apps_to_build \
            else DEFAULT_APP_DICTS_DIR
        dicts_path: str = os.path.join(app_root(app_name), dicts_dir)
        if not os.path.isdir(dicts_path):
            continue
        source_paths[app_name] = dicts_path

    for app_name, dicts_path in source_paths.items():
        app_dicts: List[str] = [
            f for f in os.listdir(dicts_path)
            if re.match(f"^[a-z][a-z](_[A-Z0-9][A-Z0-9])?.json$", f)
        ]
        for fn in app_dicts:
            fp: str = os.path.join(dicts_path, fn)
            locale_name: str = fn[:-5]
            if locale_name not in locales:
                locales[locale_name]: Locale = Locale.parse(locale_name)
            locale: Locale = locales[locale_name]

            dictionary: Dictionary = dictionaries.setdefault(locale_name, Dictionary(locale))
            dictionary.merge(dictionary.load(fp, app_name.split('.')[-1]))
            logger.info(
                f"merged translations for {CSTYLE['bold']}{locale_name}{CSTYLE['clear']} "
                f"from {CSTYLE['red']}{app_name}{CSTYLE['clear']}"
            )

    for d in dictionaries.values():
        d.save()
        logger.info(f"saved translations for {CSTYLE['bold']}{str(d.locale)}{CSTYLE['clear']}")

