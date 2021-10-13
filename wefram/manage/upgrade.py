""" The platform and applications upgrade """

from typing import *
from .. import config
from . import platform


async def run(args: List[str]) -> None:
    if not args:
        args = ['system']

    for arg in args:
        if arg == 'system' or arg == config.COREPKG:
            await platform.upgrade_system(False)
            return

