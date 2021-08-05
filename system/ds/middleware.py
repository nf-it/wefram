from starlette.types import ASGIApp, Receive, Scope, Send
from ..requests import context, routing, is_static_path
from .orm.engine import Session
from . import redis


class DatastorageConnectionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app: ASGIApp = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):
            await self.app(scope, receive, send)
            return

        for prefix in routing.static_routes_prefixes:
            if scope['path'].startswith(prefix):
                await self.app(scope, receive, send)
                return

        if is_static_path(scope['path']):
            await self.app(scope, receive, send)
            return

        async with Session() as db:
            scope['db'] = db
            context['db'] = db
            await self.app(scope, receive, send)
            await db.commit()


class RedisConnectionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        for prefix in routing.static_routes_prefixes:
            if scope['path'].startswith(prefix):
                await self.app(scope, receive, send)
                return

        if is_static_path(scope['path']):
            await self.app(scope, receive, send)
            return

        connection = await redis.create_connection()
        scope['redis'] = connection
        context['redis'] = connection
        await self.app(scope, receive, send)
        await connection.close()
