"""
Provides URL generation and handling general functions.
"""

from typing import *
from . import defaults
from .tools import get_calling_app


__all__ = [
    'asset_url'
]


def asset_url(res_name: str, app_name: Optional[str] = None) -> str:
    """ Returns the absolute URL path to the asset file basing on the given
    resource name and the corresponding parent resource's application. If
    the :argument:`app_name` omitted - the calling app will be used as
    parent app.

    Note that this function not checks the specified resource existance!

    :param res_name:
        The name of the resource file (possible with relative path).
    :type res_name:
        str

    :param app_name:
        The name of the resource parent app (the app which provides specified
        resource). If omitted - the calling app will be used.
    :type app_name:
        (optional) str

    :return:
        The absolute URL ready to use on the client side.
    :rtype:
        str
    """

    if not app_name:
        app_name = get_calling_app()
    return '/'.join([defaults.URL_STATICS, 'assets', app_name.strip('/'), res_name.strip('/')])

