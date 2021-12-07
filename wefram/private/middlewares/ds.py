from typing import *
from sqlalchemy.exc import PendingRollbackError
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from ...requests import routing, is_static_path
from ...runtime import context
from ...cli import CliMiddleware
from ...ds.orm.engine import AsyncSession
from ...ds import redis


__all__ = [
    'DatastorageConnectionMiddleware',
    'DatastorageConnectionCliMiddleware',
    'RedisConnectionMiddleware',
    'RedisConnectionCliMiddleware'
]


class DatastorageConnectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path: str = request.url.path
        for prefix in routing.static_routes_prefixes:
            if path.startswith(prefix):
                return await call_next(request)

        if is_static_path(path):
            return await call_next(request)

        async with AsyncSession() as db:
            async with db.begin():
                request.scope['db'] = db
                context['db'] = db
                response: Response = await call_next(request)
                try:
                    await db.commit()
                except PendingRollbackError:
                    pass

        return response


class RedisConnectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path: str = request.url.path
        for prefix in routing.static_routes_prefixes:
            if path.startswith(prefix):
                return await call_next(request)

        if is_static_path(path):
            return await call_next(request)

        connection = await redis.create_connection()
        request.scope['redis'] = connection
        context['redis'] = connection
        response: Response = await call_next(request)
        await connection.close()

        return response


class DatastorageConnectionCliMiddleware(CliMiddleware):
    async def __call__(self, call_next: Callable):
        async with AsyncSession() as db:
            context['db'] = db
            await call_next()
            try:
                await db.commit()
            except PendingRollbackError:
                pass


class RedisConnectionCliMiddleware(CliMiddleware):
    async def __call__(self, call_next: Callable):
        connection = await redis.create_connection()
        context['redis'] = connection
        await call_next()
        await connection.close()

