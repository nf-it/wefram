from typing import *
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from ... import config
from ...cli import CliMiddleware
from ...requests import routing
from ...runtime import context
from ...settings.routines import get


__all__ = [
    'SettingsMiddleware',
    'SettingsCliMiddleware'
]


class SettingsCliMiddleware(CliMiddleware):
    async def __call__(self, call_next: Callable) -> None:
        context['settings']: dict = {}

        for entity_name in config.SETTINGS_ALWAYS_LOADED:
            await get(entity_name)

        await call_next()


class SettingsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        for prefix in routing.static_routes_prefixes:
            if request.scope['path'].startswith(prefix):
                return await call_next(request)

        context['settings']: dict = {}

        for entity_name in config.SETTINGS_ALWAYS_LOADED:
            await get(entity_name)

        return await call_next(request)
