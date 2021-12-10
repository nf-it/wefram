from typing import *
import os
import os.path
import asyncio
import shutil
import string
import random
import getpass
import json
import sys
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import create_async_engine


def yesno(caption: Optional[str] = None, default_yes: bool = False) -> bool:
    prompt: str = (caption or "Are you sure?") + (
        " [Y|n] " if default_yes else " [y|N] "
    )
    answer: str = input(prompt)
    if not answer:
        return default_yes

    if default_yes and not answer.lower().startswith('n'):
        return True

    return answer.lower().startswith('y')


def term_input(caption: str, default: Optional[str] = None) -> str:
    placeholder: str = ' '.join([s for s in [
        caption,
        f"[{default}]" if default else None
    ] if s])
    val: Optional[str] = None
    while val is None:
        val = input(f"{placeholder}: " if placeholder else '')
        if val == '':
            val = default
    return val


def random_secret(length: int) -> str:
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(length)
    )


def json_to_file(o: Any, filename: str, **kwargs) -> None:
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('ensure_ascii', False)
    with open(filename, 'w') as f:
        json.dump(o, f, **kwargs)


DIST = [
    'manage',
    'asgi.py',
    'server.py',
    'main.tsx',
    'makefile'
]

BUILD_JSON = {
  "buildDir": ".var/build",
  "staticsDir": ".var/build/static",
  "staticsUrl": "/static",
  "assetsDir": "assets",
  "filesDir": "./var/files",
  "filesUrl": "/files"
}

APPS_JSON = []

CONFIG_JSON = {
    "project": {},
    "projectName": "wefram_based_project",
    "appTitle": "Wefram Workspace",
    "auth": {
        "salt": random_secret(64),
        "secret": random_secret(64),
        "sessionTimeoutMins": 720,
        "rememberUsername": True,
        "backends": ['local'],
    },
    "url": {
        "default": "/workspace",
        "defaultAuthenticated": "/workspace",
        "defaultGuest": "/workspace/login",
        "onLogoff": "/workspace/login",
        "loginScreen": "/workspace/login"
    },
    "db": {
        "user": "wefram",
        "pass": random_secret(64),
        "name": "wefram",
        "port": 5432,
        "migrate.dropMissingTables": True,
        "migrate.dropMissingColumns": True
    },
    "devel": True
}


async def create_database(
        sa_user: str,
        sa_password: str,
        host: str,
        port: Union[str, int],
        name: str,
        user: str,
        password: str
) -> None:
    engine = create_async_engine(
        'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'.format(
            user=sa_user,
            password=sa_password,
            host=host,
            name='postgres',
            port=port,
        ),
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as cn:
        password = password.replace("'", "\\'")
        print("Creating the database user...")
        await cn.execute(sql.text(
            f'CREATE USER "{user}" WITH PASSWORD \'{password}\''
        ))
        print("Creating the database...")
        await cn.execute(sql.text(
            f'CREATE DATABASE "{name}" WITH OWNER "{user}"'
        ))


async def _main() -> None:
    """ Runs from the command-line to prepare the very new project in the
    directory where this command been executed at. """

    print("This routine will prepare the NEW project to be used with WEFRAM platform.")
    print("This requires that you have installed at least:")
    print("  PostgreSQL server")
    print("  Redis server")
    print("")
    if not yesno("Have you made all of listed above?"):
        return

    if len(sys.argv) > 1:
        project_dir: str = sys.argv[1]
        if os.path.exists(project_dir):
            print("You have specified the project directory:")
            print(f" [{project_dir}]")
            print("but it is already exists! Cannot proceed with that.")
            return
        os.makedirs(project_dir, exist_ok=True)
        os.chdir(project_dir)

    cwd: str = os.getcwd()
    core_path: str = os.path.abspath(f"{os.path.split(__file__)[0]}/../..")

    print("")
    print("The working directory for the project is")
    print(f"  [{cwd}]")
    print("")

    print("Wefram-based project uses PostgreSQL database. Please enter its credentials.")
    db_host: str = term_input("PostgreSQL host", '127.0.0.1')
    db_name: str = term_input("Project database name", 'project')
    db_user: str = term_input("Project database user", 'projectdba')
    db_pass: str = term_input("Project database user's password", random_secret(64))

    if ':' in db_host:
        db_host, db_port = db_host.split(':', 1)
    else:
        db_port = 5432

    print("")
    print("Do you need to CREATE the specified database for the project? Instead, you")
    print("may have it been created by yourself (the best option)")
    print("")
    if yesno(f"Do create a new database `{db_name}`"):
        print("")
        print("Please specify the PostgreSQL admin user credentials (the credentials of the")
        print("user which has `createdb` and `superadmin` rights, usually `postgres`). Those")
        print("credentials will not be saved anywhere in the project, them will be used once")
        print("for creating the new database only.")
        print("")
        sa_user: str = term_input("PostgreSQL admin user name", 'postgres')
        sa_pass: str = getpass.getpass(f"The `{sa_user}` password: ")

        print("")
        print("Trying to connect the PostgreSQL database server and create a new database...")
        await create_database(
            sa_user,
            sa_pass,
            db_host,
            db_port,
            db_name,
            db_user,
            db_pass
        )

    db_port = int(db_port) if str(db_port).isdigit() else 5432

    print("")
    print("Please define the project name (not the title). This is the name you usually use")
    print("as `git` repo name or directory name for the project and defines the project")
    print("along other ones.")
    print("")
    project_name: str = term_input("Project name", (os.path.split(cwd)[-1]).replace('.', '_').replace(' ', '_'))

    print("")
    print("Please define how your project will be titled (the human readable name which")
    print("will be used in the interface)")
    app_title: str = term_input("Project caption")

    for f in DIST:
        shutil.copyfile(
            os.path.join(core_path, 'manage', 'dist', 'project', f),
            os.path.join(cwd, f)
        )

    CONFIG_JSON['db']['user'] = db_user
    CONFIG_JSON['db']['pass'] = db_pass
    CONFIG_JSON['db']['name'] = db_name
    CONFIG_JSON['db']['port'] = db_port
    CONFIG_JSON['projectName'] = project_name
    CONFIG_JSON['appTitle'] = app_title

    json_to_file(APPS_JSON, os.path.join(cwd, 'apps.json'))
    json_to_file(BUILD_JSON, os.path.join(cwd, 'build.json'))
    json_to_file(CONFIG_JSON, os.path.join(cwd, 'config.json'))

    os.chmod(os.path.join(cwd, 'manage'), 0o770)
    os.chmod(os.path.join(cwd, 'config.json'), 0o660)
    os.chmod(os.path.join(cwd, 'build.json'), 0o660)
    os.chmod(os.path.join(cwd, 'apps.json'), 0o660)

    print("")
    print("=============================================================================")
    print("")
    print("The project environment is ready to use. You may use `./manage` to manage the")
    print("basic project needs. To create the first project app, use:")
    print("")
    print("./manage app create <app_name>")
    print("")
    print("Remember to do the `make` after each app code been updated:")
    print("")
    print("./manage make")
    print("")


def execute() -> None:
    asyncio.run(_main())


if __name__ == '__main__':
    execute()

