import types
from typing import *
from .tools import app_has_module, load_app_module
from . import aaa, ds, apps, logger


__all__ = [
    'rebuild_db',
    'upload_initial_data',
    'build_demo',
]


async def dropall() -> None:
    logger.warning("Flushing REDIS database!")
    redis_cn: ds.redis.RedisConnection = await ds.redis.create_connection()
    await redis_cn.flushall()

    logger.warning("Dropping tables in the PostgreSQL database!")
    await ds.migrate.dropall()


async def rebuild_db() -> None:
    await dropall()

    logger.warning("Creating tables in the PostgreSQL database!")
    await ds.migrate.migrate()

    logger.warning("Uploading initial AAA data to the PostgreSQL database")
    async with ds.orm.engine.AsyncSession() as cn:
        roles: dict = {
            'admins': aaa.Role(
                name='Administrators',
                permissions=[p.key for p in aaa.permissions.registered]
            ),
            'users': aaa.Role(
                name='All users'
            )
        }
        [cn.add(r) for r in roles.values()]

        users: dict = {
            'root': aaa.User(
                login='root',
                secret=aaa.hash_password('qwerty'),
                first_name='Administrator'
            ),
            'user': aaa.User(
                login='user',
                secret=aaa.hash_password('1234'),
                first_name='The user'
            ),
        }

        users['root'].roles.append(roles['admins'])
        users['root'].roles.append(roles['users'])

        [cn.add(u) for u in users.values()]

        await cn.commit()


async def upload_initial_data() -> None:
    logger.warning("Uploading initial apps data to the PostgreSQL database")
    async with ds.orm.engine.AsyncSession() as cn:
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


async def build_demo() -> None:
    from manage import demos
    await demos.build()

