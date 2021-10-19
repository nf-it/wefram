import asyncio
from types import ModuleType
from typing import *
import os
import shutil
from . import apps, logger, config, runtime
from .tools import CSTYLE, load_app_module, json_from_file, json_to_file, app_root, app_has_module, has_app


__all__ = [
    'drop',
    'setup',
    'demo',
    'remove',
    'enable',
    'disable'
]


async def drop() -> None:
    from . import ds

    logger.warning("Flushing REDIS database!")
    redis_cn: ds.redis.RedisConnection = await ds.redis.create_connection()
    await redis_cn.flushall()

    logger.warning("Dropping tables in the PostgreSQL database!")
    await ds.migrate.dropall()

    logger.warning("Dropping uploaded files")
    shutil.rmtree(config.FILES_ROOT, ignore_errors=True)
    os.makedirs(config.FILES_ROOT, exist_ok=True)


async def _setup() -> None:
    from . import aaa
    from .models import User, Role

    cn = runtime.context['db']

    roles: dict = {
        'admins': Role(
            name='Administrators',
            permissions=[p.key for p in aaa.permissions.registered]
        ),
        'users': Role(
            name='All users'
        )
    }
    [cn.add(r) for r in roles.values()]

    users: dict = {
        'root': User(
            login='root',
            secret=aaa.hash_password('qwerty'),
            first_name='Administrator'
        ),
        'user': User(
            login='user',
            secret=aaa.hash_password('1234'),
            first_name='The user'
        ),
    }

    users['root'].roles.append(roles['admins'])
    users['root'].roles.append(roles['users'])

    [cn.add(u) for u in users.values()]

    logger.warning("Setting up installed and enabled apps")

    enabled_apps: List[str] = apps.get_apps_loaded()
    for appname in enabled_apps:
        appmodule: ModuleType = apps.modules[appname]
        if not app_has_module(appmodule, 'setup'):
            continue
        app_setup: ModuleType = load_app_module(appmodule, 'setup')
        if not hasattr(app_setup, 'setup'):
            continue
        logger.info(f"setting up app [{appname}]")
        f = getattr(app_setup, 'setup')
        await f()


async def setup() -> None:
    from . import ds

    print("\n\nSETUP procedure initialized, setting the project up\n\n")

    await drop()

    logger.warning("Creating tables in the PostgreSQL database!")
    await ds.migrate.migrate()

    logger.warning("Setting up the project")
    await runtime.within_cli(_setup)


async def _demo(app_to_build: Optional[str] = None) -> None:
    apps_to_build: List[str] = ['system'] + config.APPS_ENABLED if not app_to_build else [app_to_build]
    for appname in apps_to_build:
        appmodule: ModuleType = apps.modules[appname]
        if not app_has_module(appmodule, 'setup'):
            continue
        app_setup: ModuleType = load_app_module(appmodule, 'setup')
        if not hasattr(app_setup, 'setup_demo'):
            continue
        logger.info(f"setting up app's demo [{appname}]")
        f = getattr(app_setup, 'setup_demo')
        await f()


async def demo(app_to_build: Optional[str] = None) -> None:
    logger.warning("Settings up the project demo")
    await runtime.within_cli(_demo, app_to_build)


async def remove(apps_to_remove: List[str]) -> None:
    print("Updating `apps.json` file")
    apps_json_filename: str = os.path.join(config.PRJ_ROOT, 'apps.json')
    json_to_file([
        app for app in json_from_file(apps_json_filename) if app not in apps_to_remove
    ], apps_json_filename, indent=2)

    for app in apps_to_remove:
        if not app_has_module(app, 'setup'):
            continue
        app_setup: ModuleType = load_app_module(app, 'setup')
        uninstall_func: Optional[callable] = getattr(app_setup, 'on_uninstall')
        if not uninstall_func or not callable(uninstall_func):
            continue
        print(f"Executing `uninstall` for: {app}")
        if asyncio.iscoroutinefunction(uninstall_func):
            await uninstall_func()
        else:
            uninstall_func()

    for app in apps_to_remove:
        print(f"Removing app directory: {app}")
        shutil.rmtree(app_root(app))


async def enable(apps_to_enable: List[str]) -> None:
    for app in apps_to_enable:
        if has_app(app):
            continue
        raise ModuleNotFoundError(f"app `{app}` is not installed")

    apps_json_filename: str = os.path.join(config.PRJ_ROOT, 'apps.json')
    apps_json: list = json_from_file(apps_json_filename)

    to_enable: List[str] = []
    for app in apps_to_enable:
        if app in apps_json:
            continue
        to_enable.append(app)
        apps_json.append(app)

    apps_order: Dict[str, int] = apps.get_order_for(apps_json)
    apps_json = sorted(apps_json, key=lambda n: apps_order.get(n, 99999) or 99999)

    json_to_file(apps_json, apps_json_filename, indent=2)

    for app in to_enable:
        if not app_has_module(app, 'setup'):
            continue
        app_setup: ModuleType = load_app_module(app, 'setup')
        enable_func: Optional[callable] = getattr(app_setup, 'on_enable')
        if not enable_func or not callable(enable_func):
            continue
        print(f"Executing `enable` for: {app}")
        if asyncio.iscoroutinefunction(enable_func):
            await enable_func()
        else:
            enable_func()


async def disable(apps_to_disable: List[str]) -> None:
    for app in apps_to_disable:
        if has_app(app):
            continue
        raise ModuleNotFoundError(f"app `{app}` is not installed")

    apps_json_filename: str = os.path.join(config.PRJ_ROOT, 'apps.json')
    json_to_file([
        app for app in json_from_file(apps_json_filename) if app not in apps_to_disable
    ], apps_json_filename, indent=2)

    for app in apps_to_disable:
        if not app_has_module(app, 'setup'):
            continue
        app_setup: ModuleType = load_app_module(app, 'setup')
        disable_func: Optional[callable] = getattr(app_setup, 'on_disable')
        if not disable_func or not callable(disable_func):
            continue
        print(f"Executing `disable` for: {app}")
        if asyncio.iscoroutinefunction(disable_func):
            await disable_func()
        else:
            disable_func()

