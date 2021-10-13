from typing import *
import os
import os.path
import shutil
from ..routines.tools import term_input, term_choice
from ... import config
from ...tools import has_app, app_root


__all__ = [
    'create_container'
]


CONTAINERS_TYPES: dict = {
    'BaseScreen': 'Base screen',
    'EntityCard': 'Entity card',
    'EntityListScreen': 'Entity list screen',
    'EntityTableScreen': 'Entity table screen',
    'EntityListScreen@Card': 'Entity list screen with windowed Card container attached',
    'EntityTableScreen@Card': 'Entity table screen with windowed Card container attached'
}


def create_container(params: List[str]) -> None:
    if len(params) != 2:
        print("Invalid syntax, expected: `manage app frontend.create-container <app_name> <container_name>`")
        return

    app: str
    container_name: str
    app, container_name = params

    if not has_app(app):
        print(f"Application `{app}` is not installed!")
        return

    root: str = app_root(app)

    container_default_root: str = 'frontend/containers'
    container_dir: str = term_input("Container relative root path", container_default_root)
    container_dir: str = os.path.join(root, container_dir)
    if not os.path.isdir(container_dir):
        os.makedirs(container_dir, exist_ok=True)

    container_type: str = term_choice("Container type", CONTAINERS_TYPES)
    skel_path: str = os.path.join(config.CORE_ROOT, 'skel', 'frontend', container_type)
    foldered: bool = os.path.isdir(skel_path)
    src_path: str = skel_path if foldered else f"{skel_path}.tsx"

    replaces: dict = {}
    if container_type.startswith('Entity'):
        replaces['###entity###'] = term_input("Corresponding API entity name")

    if container_type in ('EntityListWithCardScreen', 'EntityTableWithCardScreen'):
        card_container: str = term_input(
            'Attaching card container path (ex: "frontend/containers/MyCard")'
        )
        card_container_path: str = os.path.join(root, card_container)
        if not os.path.isdir(card_container_path) and not os.path.isfile(f"{card_container_path}.tsx"):
            print("ERROR: specified card container does not exists! Please create it first!")
            exit(2)
        card_container_importpath: str = f'{app}/{card_container}' \
            if app != 'system' and app != 'wefram' \
            else f'system/{card_container}'
        replaces["import CardContainer from './EntityCard'"] = f"import CardContainer from '{card_container_importpath}'"

    container_dest: str = os.path.join(container_dir, (container_name if foldered else f"{container_name}.tsx"))
    if os.path.exists(container_dest):
        print(f"Specified container is already exists: {container_name}!")
        exit(3)

    if foldered:
        shutil.copytree(src_path, container_dest)
    else:
        shutil.copy2(src_path, container_dest)

    container_tsx_file: str = os.path.join(container_dest, 'index.tsx') if foldered else container_dest
    with open(os.path.join(container_tsx_file), 'r') as f:
        c = f.read()

    c = c.replace('___', container_name).replace('###app###', app)
    for f, t in replaces.items():
        c = c.replace(f, t)

    with open(os.path.join(container_tsx_file), 'w') as f:
        f.write(c)

    print("done!")

