from typing import *
from starlette.types import ASGIApp, Receive, Scope, Send
import config
from .. import middlewares
from ..cli import CliMiddleware
from ..requests import routing
from ..runtime import context
from .models import SettingsCatalog
from .routines import get


__all__ = [
    'SettingsMiddleware',
    'SettingsCliMiddleware'
]


@middlewares.register_for_cli
class SettingsCliMiddleware(CliMiddleware):
    async def __call__(self, call_next: Callable) -> None:
        context['settings']: Dict[str, SettingsCatalog] = {}

        for entity_name in config.SETTINGS_ALWAYS_LOADED:
            await get(entity_name)

        await call_next()


class SettingsMiddleware:
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

        context['settings']: Dict[str, SettingsCatalog] = {}

        for entity_name in config.SETTINGS_ALWAYS_LOADED:
            await get(entity_name)

        await self.app(scope, receive, send)
