from typing import *
from . import config
from .tools import get_calling_app


__all__ = [
    'media_res_url'
]


def media_res_url(res_name: str, app_name: Optional[str] = None) -> str:
    if not app_name:
        app_name = get_calling_app()
    return '/'.join([config.STATICS_URL, 'media', app_name.strip('/'), res_name.strip('/')])

