import os
import os.path
from ... import config


__all__ = [
    'run',
    'DIRTREE'
]


DIRTREE = [
    config.STATICS_ROOT,
    config.BUILD_ROOT,
    os.path.join(config.BUILD_ROOT, 'frontend')
]


def run(*_) -> None:
    for d in DIRTREE:
        os.makedirs(d, exist_ok=True)

