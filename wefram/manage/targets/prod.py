"""
Provides the ability to make everything for the production, but without
deployment facility. This might be useful if the current configuration or
the environment has DEBUG enabled, but you want to build the project
in the PRODUCTION mode instead.
"""

from ... import config, logger
from . import all


async def run(*_) -> None:
    logger.set_level(logger.WARNING)
    config.PRODUCTION = True

    await all.run(*_)

