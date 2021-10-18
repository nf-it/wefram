""" Project-level management """

from typing import *
import os.path
import shutil
from ..routines.tools import term_input, term_intinput, yesno
from ...tools import CSTYLE
from ...types.apps import Manifest
from ... import config, setups


def create(args: List[str]) -> None:
    """ Creates new app in the project with the already ready structure. """

    if not args:
        print("Syntax error, expected: `manage app create <app_name>`")
        return

    app: str = args.pop(0)
    root: str = os.path.join(config.PRJ_ROOT, app)
    if os.path.exists(root):
        print(f"app '{app}' is already exists!")
        print(f"{CSTYLE['red']}[!] FAILED{CSTYLE['clear']}")
        exit(1)

    caption: str = term_input("The new app's caption")
    order: int = term_intinput("The new app's order (number from 0 upto 99999)", 0)

    shutil.copytree(os.path.join(config.CORE_ROOT, 'skel', 'app'), root)
    Manifest(
        name=app,
        caption=caption,
        order=order or None,
        requirements={
            'pip': {},
            'node': {}
        }
    ).write(
        os.path.join(root, 'manifest.json')
    )

    print(f"{CSTYLE['yellow']}[!] do NOT forget to include new app into 'apps.json' [!]{CSTYLE['clear']}")
    print(f"{CSTYLE['green']}[V] OK{CSTYLE['clear']}")


async def remove(args: List[str]) -> None:
    """ Removes the specified applications from the project. More than one app at
    one time is supported. """

    if not args:
        print("Syntax error, expected: `manage app remove <app_name> [app_name] [...]`")
        return

    if not yesno(
            f"You about to remove next app(s): {CSTYLE['red']}{', '.join(args)}{CSTYLE['clear']}; are you sure?",
            default_yes=False
    ):
        print("Cancelled")
        return

    await setups.remove(args)
    print("done")


async def enable(args: List[str]) -> None:
    """ Adds specified apps into the `apps.json` file, using the specified apps' order """

    if not args:
        print("Syntax error, expected: `manage app enable <app_name> [app_name] [...]`")
        return

    await setups.enable(args)
    print("done")


async def disable(args: List[str]) -> None:
    """ Removes specified apps from the `apps.json` file """

    if not args:
        print("Syntax error, expected: `manage app disable <app_name> [app_name] [...]`")
        return

    await setups.disable(args)
    print("done")

