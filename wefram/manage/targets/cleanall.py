import shutil
import os
import os.path
from . import dirtree


__all__ = [
    'run'
]


DIRTREE = dirtree.DIRTREE


def run(*_) -> None:
    for d in DIRTREE:
        if not os.path.exists(d):
            continue
        shutil.rmtree(d, ignore_errors=True)
    dirtree.run()

