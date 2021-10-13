from typing import *
import shutil
import os
import os.path
from ... import config, logger, tools


__all__ = [
    'run'
]


BUILD_TEXTS_ROOT: str = os.path.join(config.BUILD_ROOT, 'texts')


def path_from_root(root: str) -> Optional[str]:
    try:
        return tools.module_path(root)
    except ModuleNotFoundError:
        return None


def run(roots: List[str]) -> None:
    shutil.rmtree(BUILD_TEXTS_ROOT, ignore_errors=True)
    os.makedirs(BUILD_TEXTS_ROOT)
    logger.info(f"building texts assets")
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        fqpath: str = os.path.join(rootpath, 'assets', 'texts')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building texts assets => {root}")
        shutil.copytree(fqpath, os.path.join(BUILD_TEXTS_ROOT, root))
