from typing import *


def print_help() -> None:
    print("")


async def test_run() -> None:
    from .routines.project import ensure_apps_loaded

    ensure_apps_loaded()


async def run(args: List[str]) -> None:
    if not args:
        print_help()
        return

    command = args.pop(0)

    if command == 'run':
        print("(test run)")
        print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        print("")

        await test_run()

        print("")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        return

    print("(test)")
