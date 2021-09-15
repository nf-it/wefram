import os
import os.path
import shutil
from argparse import Namespace
from manage import tools
import config


CONTAINERS_TYPES: dict = {
    'BaseScreen': 'Base screen',
    'EntityCard': 'Entity card',
    'EntityListScreen': 'Entity list screen',
    'EntityTableScreen': 'Entity table screen',
    'EntityListScreen@Card': 'Entity list screen with windowed Card container attached',
    'EntityTableScreen@Card': 'Entity table screen with windowed Card container attached'
}


async def runcmd(command: str, args: Namespace) -> None:

    if command == 'create-container':
        app_name: str = tools.term_input("Target APP name")
        app_root: str = config.COREROOT \
            if app_name == 'system' \
            else os.path.join(config.APPSROOT, app_name)
        if not os.path.isdir(app_root):
            print(f"typed app [{app_name}] is not exists, do 'manage create-app' first!")
            exit(2)

        container_name: str = tools.term_input("New container name")
        if not container_name:
            print("failed: container name is required!")
            exit(2)

        container_default_root: str = 'frontend/containers'
        container_dir: str = tools.term_input("Container relative root path", container_default_root)
        container_dir: str = os.path.join(app_root, container_dir)
        if not os.path.isdir(container_dir):
            os.makedirs(container_dir, exist_ok=True)

        container_type: str = tools.term_choice("Container type", CONTAINERS_TYPES)
        skel_path: str = os.path.join(config.COREROOT, 'skel', 'frontend', container_type)
        foldered: bool = os.path.isdir(skel_path)
        src_path: str = skel_path if foldered else f"{skel_path}.tsx"

        replaces: dict = {}
        if container_type.startswith('Entity'):
            replaces['###entity###'] = tools.term_input("Corresponding API entity name")

        if container_type in ('EntityListWithCardScreen', 'EntityTableWithCardScreen'):
            card_container: str = tools.term_input(
                'Attaching card container path (ex: "frontend/containers/MyCard")'
            )
            card_container_path: str = os.path.join(app_root, card_container)
            if not os.path.isdir(card_container_path) and not os.path.isfile(f"{card_container_path}.tsx"):
                print("ERROR: specified card container does not exists! Please create it first!")
                exit(2)
            card_container_importpath: str = f'{app_name}/{card_container}' \
                if app_name != 'system' \
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

        c = c.replace('___', container_name).replace('###app###', app_name)
        for f, t in replaces.items():
            c = c.replace(f, t)

        with open(os.path.join(container_tsx_file), 'w') as f:
            f.write(c)

        print("done!")
        exit(0)

    print(f"Unknown frontend command: {command}")
    exit(1)

