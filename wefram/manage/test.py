import types
import asyncio
from typing import *
from wefram import tools, runtime


def print_help() -> None:
    print("")


async def test_run() -> None:
    from .routines.project import ensure_apps_loaded

    ensure_apps_loaded()


async def test_app(command: str, args: List[str]) -> None:
    from wefram import apps

    app: str = command
    if app != 'system' and app != 'wefram' and not apps.is_enabled(app):
        print(f"app '{app}' is not enabled and cannot be tested")
        return

    tests: types.ModuleType = tools.load_app_module(app, 'tests')
    if tests is None:
        print(f"app '{app}' has no module named 'tests' (tests.py) to be ran within test")
        return

    test_name: str = args.pop(0) if len(args) else 'main'
    if not hasattr(tests, test_name):
        print(f"app '{app}' has no test named '{test_name}' in the 'tests' module")
        return

    test = getattr(tests, test_name)
    if asyncio.iscoroutinefunction(test):
        await test(*args)
    else:
        test(args)


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

    else:
        await runtime.within_cli(test_app, command, args)
        return
