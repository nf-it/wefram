from typing import *
from types import ModuleType
import os
import os.path
import importlib
import asyncio


__all__ = [
    'exec_with_args'
]


EXCLUDED = [
    'targets',
    'routines',
    'dist',
    'platform'
]

PRIVATE = [
    'platform'
]


def get_facilities() -> List[str]:
    management_path: str = os.path.split(os.path.abspath(__file__))[0]
    return sorted([
        (f[:-3] if f.endswith('.py') else f) for f in os.listdir(management_path)
        if f[:-3] not in EXCLUDED and f not in EXCLUDED
        and (f.endswith('.py') or os.path.isfile(os.path.join(management_path, f, '__init__.py')))
        and not f.startswith('_')
        and not f.endswith('_')
    ])


def print_help() -> None:
    print("\nWefram management available commands are:")
    [print(f"  {f}") for f in get_facilities()]
    print("")


async def main(args: list) -> None:
    if not args:
        print_help()
        return

    command = args.pop(0)

    if (command in EXCLUDED and command not in PRIVATE) \
            or command.startswith('_') \
            or command.endswith('_'):
        print(f"Unsupported command given: {command}")
        return

    # try:
    facility: ModuleType = importlib.import_module('.'.join(['wefram', 'manage', command]))

    # except ModuleNotFoundError:
    #     print(f"Unsupported command given: {command}")
    #     return

    run: callable = getattr(facility, 'run')
    await run(args)


def exec_with_args(args: list) -> None:
    asyncio.run(main(args[1:]))
