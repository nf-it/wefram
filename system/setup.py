import types
from typing import *
from .tools import app_has_module, load_app_module, term_input, term_choice
from . import aaa, ds, apps, logger


__all__ = [
    'rebuild_db',
    'upload_initial_data',
    'build_demo',
]


async def rebuild_db() -> None:
    logger.warning("Flushing REDIS database!")
    redis_cn: ds.redis.RedisConnection = await ds.redis.create_connection()
    await redis_cn.flushall()

    logger.warning("Dropping and creating tables in the PostgreSQL database!")
    async with ds.orm.engine.engine.begin() as cn:
        await cn.run_sync(ds.Model.metadata.drop_all)
        await cn.run_sync(ds.Model.metadata.create_all)

    logger.warning("Uploading initial AAA data to the PostgreSQL database")
    async with ds.orm.engine.Session() as cn:
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
    async with ds.orm.engine.Session() as cn:
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
    from . import demo

    await rebuild_db()
    await demo.build()

