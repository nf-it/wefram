import aioredis
from aioredis import Redis as RedisConnection
from .. import config
from ..runtime import context


__all__ = [
    'create_connection',
    'get_connection',
    'close_connection',
    'RedisConnection'
]


async def create_connection() -> RedisConnection:
    """ Makes a new connection to the REDIS database and returns connection to the caller. """
    return aioredis.from_url(
        config.REDIS['uri'],
        password=config.REDIS['password'],
        encoding='utf-8'
    )


async def get_connection() -> RedisConnection:
    """ Connects to the REDIS database end returns that connection to the caller. If the routine being
    called within ASGI environment - uses the ASGI context instead of new connection.
    """

    if 'redis' not in context:
        context['redis'] = await create_connection()

    return context['redis']


async def close_connection(connection: RedisConnection = None) -> None:

    if not connection:
        if 'redis' not in context:
            return
        connection = context['redis']

    await connection.close()

