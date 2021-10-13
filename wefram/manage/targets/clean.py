import shutil
import os
import os.path
from ... import config


__all__ = [
    'run'
]


TREE = [
    config.STATICS_ROOT,
    config.BUILD_ROOT
]
EXCLUDE = []


def run(*_) -> None:
    [
        shutil.rmtree(os.path.join(config.STATICS_ROOT, f), ignore_errors=True)
        for f in os.listdir(config.STATICS_ROOT)
        if os.path.isdir(f) and f not in EXCLUDE
    ]
