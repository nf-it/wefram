from typing import *
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import HTTPConnection
import babel
import config
from ..requests import context, is_static_path
from .funcs import best_matching_locale
from .locales import Locale


__all__ = ['LocalizationMiddleware']


class LocalizationMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        from ..aaa import UnauthenticatedUser, SessionUser
        from ..requests import routing

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

        selected_locale: Optional[Locale] = None
        if 'user' in context and not isinstance(context['user'], UnauthenticatedUser):
            user: SessionUser = context['user']
            if user.locale:
                try:
                    selected_locale = Locale.parse(user.locale)
                except babel.UnknownLocaleError:
                    pass

        if not selected_locale:
            conn = HTTPConnection(scope)
            if 'accept-language' in conn.headers and conn.headers['accept-language']:
                locales_preferred: List[str] = await self.parse_accept_language(conn.headers['accept-language'])
                locale_preferred: Optional[babel.Locale] = best_matching_locale(locales_preferred)

                if locale_preferred:
                    selected_locale = locale_preferred

                else:
                    selected_locale = Locale.parse(config.DEFAULT_LOCALE)
            else:
                selected_locale = Locale.parse(config.DEFAULT_LOCALE)

        context['locale']: Locale = selected_locale
        await self.app(scope, receive, send)

    async def parse_accept_language(self, header: str) -> List[str]:
        """ 
        This code been got from the resource:
            https://siongui.github.io/2012/10/11/python-parse-accept-language-in-http-request-header/
            Author: Siong-Ui Te 
        """
        languages: List[str] = header.split(',')
        locale_q_pairs: List[tuple] = []
        for language in languages:
            if language.split(';')[0] == language:
                locale_q_pairs.append((language.strip(), '1'))
            else:
                locale = language.split(';')[0].strip()
                q = language.split(';')[1].split('=')[1]
                locale_q_pairs.append((locale, q))
        return [x[0] for x in sorted(locale_q_pairs, key=lambda x: float(x[1]), reverse=True)]

