from typing import *
from types import ModuleType
import os
import re
import shutil
from ...tools import CSTYLE, app_root, app_name
from ... import logger
from ...l10n.locales import Locale
from ...l10n.catalog import Dictionary
from ...l10n.config import GENERAL_DICTS_PATH, BUILT_DICTS_PATH


__all__ = [
    'run'
]


APP_DICTS_DIR: str = 'assets/l10n'


def run(roots: List[str]) -> None:
    shutil.rmtree(BUILT_DICTS_PATH, ignore_errors=True)
    os.makedirs(BUILT_DICTS_PATH, exist_ok=True)

    locales: Dict[str, Locale] = dict()
    dictionaries: Dict[str, Dictionary] = dict()

    source_paths: Dict[str, str] = dict()
    if os.path.isdir(GENERAL_DICTS_PATH):
        source_paths['*'] = GENERAL_DICTS_PATH

    for root in roots:
        rootpath: Optional[str] = app_root(root)
        if not rootpath:
            continue
        dicts_path: Optional[str] = os.path.join(rootpath, APP_DICTS_DIR)
        if not os.path.isdir(dicts_path):
            continue
        source_paths[root] = dicts_path

    for root, dicts_path in source_paths.items():
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
            dictionary.merge(dictionary.load(fp, root.split('.')[-1]))
            logger.info(
                f"merged translations for {CSTYLE['bold']}{locale_name}{CSTYLE['clear']} "
                f"from {CSTYLE['red']}{root}{CSTYLE['clear']}"
            )
        if '*' not in root:
            text_locales: List[str] = [
                f for f in os.listdir(dicts_path)
                if os.path.isdir(os.path.join(dicts_path, f)) and re.match(f"^[a-z][a-z](_[A-Z0-9][A-Z0-9])?", f)
            ]
            for tl in text_locales:
                tl_src: str = os.path.join(dicts_path, tl)
                tl_dst: str = os.path.join(BUILT_DICTS_PATH, root, tl)
                os.makedirs(tl_dst, exist_ok=True)
                shutil.copytree(tl_src, tl_dst, dirs_exist_ok=True)
                logger.info(
                    f"copied localized texts for {CSTYLE['bold']}{root}.{tl}{CSTYLE['clear']}"
                )

    for d in dictionaries.values():
        d.save()
        logger.info(f"saved translations for {CSTYLE['bold']}{str(d.locale)}{CSTYLE['clear']}")

