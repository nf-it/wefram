from typing import *
import os
import os.path
import config
import shutil
from .tools import CSTYLE, term_input, term_intinput, term_choice


__all__ = [
    'create_app',
    'create_screen'
]


def _get_gettextable_str(caption: str, default: Optional[str] = None) -> str:
    return term_input(caption, default)


def create_app() -> None:
    """ Creates new app in the project with the already ready structure. """

    app_name: str = term_input("New app name")
    app_root: str = os.path.join(config.APPSROOT, app_name)
    if os.path.exists(app_root):
        print(f"app '{app_name}' is already exists!")
        print(f"{CSTYLE['red']}[!] FAILED{CSTYLE['clear']}")
        exit(1)

    app_caption: str = _get_gettextable_str("The new app's caption")
    app_order: int = term_intinput("The new app's order (number from 0 upto 99999)", 0)

    shutil.copytree(os.path.join(config.COREROOT, '../system/skel', 'app'), app_root)

    with open(os.path.join(app_root, 'app.py'), 'r') as f:
        content: str = f.read()
    content = content.replace('CAPTION = ...\n', f'CAPTION = "{app_caption}"\n')
    content = content.replace('ORDER = ...\n', f'ORDER = {app_order}\n' if app_order else '')
    with open(os.path.join(app_root, 'app.py'), 'w') as f:
        f.write(content)

    print(f"{CSTYLE['yellow']}[!] do NOT forget to include new app into 'apps.json' [!]{CSTYLE['clear']}")
    print(f"{CSTYLE['green']}[V] OK{CSTYLE['clear']}")


def create_screen() -> None:
    pass

