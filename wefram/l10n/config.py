import os.path
from .. import config


__all__ = [
    'GENERAL_DICTS_PATH',
    'BUILT_DICTS_PATH',
    'BUILT_TEXTS_PATH'
]


GENERAL_DICTS_PATH: str = os.path.join(config.ASSETS_ROOT, 'l10n')
BUILT_DICTS_PATH: str = os.path.join(config.BUILD_ROOT, 'l10n')
BUILT_TEXTS_PATH: str = os.path.join(config.BUILD_ROOT, 'texts')

