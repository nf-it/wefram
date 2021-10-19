""" A shortcut for making all targets for the setup in the order they best to be made.
The difference with 'all' is that some work must not be done here because it might be
done before by the :py:func:`wefram.setups.setup()` routine.
"""

from typing import *
from types import ModuleType
import asyncio
import importlib
from ...tools import CSTYLE
from ... import config, logger


ALL_TARGETS: List[str] = [
    'cleanall',
    'pip',
    'assets',
    'l10n',
    'texts',
    'screens',
    'webpack',
    'react',
]


async def run(roots: List[str]) -> None:
    for target in ALL_TARGETS:
        logger.info(f"making the target: {CSTYLE['bold']}{target}{CSTYLE['clear']}", 'make')
        try:
            target_module: ModuleType = importlib.import_module('.'.join([config.COREPKG, 'manage', 'targets', target]))

        except ModuleNotFoundError as exc:
            raise RuntimeError(
                f"Cannot find facility serves the make target '{target}'!"
            ) from exc

        makefunc: callable = getattr(target_module, 'run')
        if asyncio.iscoroutinefunction(makefunc):
            await makefunc(roots)
        else:
            makefunc(roots)
