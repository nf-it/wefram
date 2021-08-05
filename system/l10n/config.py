import os.path
import config


__all__ = [
    'GENERAL_DICTS_PATH',
    'BUILT_DICTS_PATH'
]


GENERAL_DICTS_PATH: str = os.path.join(config.ASSETS_ROOT, 'l10n')
BUILT_DICTS_PATH: str = os.path.join(config.STATICS_ROOT, 'l10n')

