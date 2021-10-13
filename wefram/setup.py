import inspect
import asyncio
import types
from typing import *
import os
import shutil
import importlib
from . import aaa, ds, apps, logger, config
from .tools import CSTYLE, load_app_module, json_from_file, json_to_file, app_root, app_has_module, has_app
from .private.models.aaa import User, Role


__all__ = [
    'drop',
    'setup',
    'demo',
    'remove',
    'enable',
    'disable'
]


async def drop() -> None:
    logger.warning("Flushing REDIS database!")
    redis_cn: ds.redis.RedisConnection = await ds.redis.create_connection()
    await redis_cn.flushall()

    logger.warning("Dropping tables in the PostgreSQL database!")
    await ds.migrate.dropall()

    logger.warning("Dropping uploaded files")
    shutil.rmtree(config.FILES_ROOT, ignore_errors=True)
    os.makedirs(config.FILES_ROOT, exist_ok=True)


async def setup() -> None:
    await drop()

    logger.warning("Creating tables in the PostgreSQL database!")
    await ds.migrate.migrate()

    logger.warning("Uploading initial AAA data to the PostgreSQL database")
    async with ds.orm.engine.AsyncSession() as cn:
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

        logger.warning("Uploading initial apps data to the PostgreSQL database")

        enabled_apps: List[str] = apps.get_apps_loaded()
        for appname in enabled_apps:
            appmodule: types.ModuleType = apps.modules[appname]
            if not app_has_module(appmodule, 'setup'):
                continue
            app_setup: types.ModuleType = load_app_module(appmodule, 'setup')
            if not hasattr(app_setup, 'upload_initial'):
                continue
            logger.info(f"uploading initial data for app [{appname}]")
            f = getattr(app_setup, 'upload_initial')
            await f(cn)

        await cn.commit()


async def demo(app_to_build: Optional[str] = None) -> None:
    apps_to_build: List[str] = ['system'] + config.APPS_ENABLED if not app_to_build else [app_to_build]
    for app in apps_to_build:
        app_main: types.ModuleType = apps.mains.get(app)
        if not app_main:
            continue
        if not hasattr(app_main, 'demo'):
            continue
        demo_target: Union[Callable, types.ModuleType] = getattr(app_main, 'demo')
        if isinstance(demo_target, types.ModuleType):
            demo_target: Callable = getattr(demo_target, 'build', None)
            if not demo_target:
                continue
        logger.info(
            f"making {CSTYLE['bold']}demo{CSTYLE['clear']} for {CSTYLE['red']}{app}{CSTYLE['clear']}"
        )
        await demo()


async def remove(apps_to_remove: List[str]) -> None:
    print("Updating `apps.json` file")
    apps_json_filename: str = os.path.join(config.PRJ_ROOT, 'apps.json')
    json_to_file([
        app for app in json_from_file(apps_json_filename) if app not in apps_to_remove
    ], apps_json_filename, indent=2)

    for app in apps_to_remove:
        if not app_has_module(app, 'setup'):
            continue
        app_setup: types.ModuleType = load_app_module(app, 'setup')
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
    apps_json = sorted(apps_json, key=lambda n: apps_order.get(n, 99999))

    json_to_file(apps_json, apps_json_filename, indent=2)

    for app in to_enable:
        if not app_has_module(app, 'setup'):
            continue
        app_setup: types.ModuleType = load_app_module(app, 'setup')
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
        app_setup: types.ModuleType = load_app_module(app, 'setup')
        disable_func: Optional[callable] = getattr(app_setup, 'on_disable')
        if not disable_func or not callable(disable_func):
            continue
        print(f"Executing `disable` for: {app}")
        if asyncio.iscoroutinefunction(disable_func):
            await disable_func()
        else:
            disable_func()

