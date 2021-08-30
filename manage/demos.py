import types
from typing import *
from system import apps, logger
from system.tools import CSTYLE
import config


__all__ = [
    'build'
]


async def build(app_name: Optional[str] = None) -> None:
    apps_to_build: List[str] = ['system'] + config.APPS_ENABLED if not app_name else [app_name]
    for app_name in apps_to_build:
        app_main: types.ModuleType = apps.mains.get(app_name)
        if not app_main:
            continue
        if not hasattr(app_main, 'demo'):
            continue
        demo: Union[Callable, types.ModuleType] = getattr(app_main, 'demo')
        if isinstance(demo, types.ModuleType):
            demo: Callable = getattr(demo, 'build', None)
            if not demo:
                continue
        logger.info(
            f"making {CSTYLE['bold']}demo{CSTYLE['clear']} for {CSTYLE['red']}{app_name}{CSTYLE['clear']}"
        )
        await demo()

