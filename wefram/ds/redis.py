"""
Provides Redis in-memory database connections functionality.

Redis is primaryly used to cache often used data in memory and store current
project state.

The example of the Redis usage is storing users' sessions
(again, for example).
"""

import aioredis
from aioredis import Redis as RedisConnection
from .. import config
from ..runtime import context


__all__ = [
    'create_connection',
    'get_connection',
    'RedisConnection',
    'pool',
    'disconnect'
]


pool: aioredis.ConnectionPool = aioredis.ConnectionPool.from_url(
    config.REDIS['uri'],
    password=config.REDIS['password'],
    encoding='utf-8'
)


async def create_connection() -> RedisConnection:
    """ Makes a new connection to the REDIS database and returns connection to the caller. """

    return RedisConnection(connection_pool=pool)


async def get_connection() -> RedisConnection:
    """ Connects to the REDIS database end returns that connection to the caller. If the routine being
    called within ASGI environment - uses the ASGI context instead of new connection.
    """

    if 'redis' not in context:
        context['redis'] = await create_connection()

    return context['redis']


async def disconnect() -> None:
    await pool.disconnect()


