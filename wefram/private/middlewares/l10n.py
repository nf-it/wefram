from typing import *
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request, HTTPConnection
from starlette.responses import Response
from starlette.authentication import UnauthenticatedUser
import babel
from ...requests import is_static_path
from ...runtime import context
from ...cli import CliMiddleware
from ... import config
from ...l10n.funcs import best_matching_locale
from ...l10n.locales import Locale


__all__ = [
    'LocalizationMiddleware',
    'LocalizationCliMiddleware'
]


class LocalizationCliMiddleware(CliMiddleware):
    async def __call__(self, call_next: Callable) -> None:
        context['locale']: Locale = Locale.parse(config.DEFAULT_LOCALE)
        await call_next()


class LocalizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        from ...models import SessionUser
        from ...requests import routing

        for prefix in routing.static_routes_prefixes:
            if request.scope['path'].startswith(prefix):
                return await call_next(request)

        if is_static_path(request.scope['path']):
            return await call_next(request)

        selected_locale: Optional[Locale] = None
        if 'user' in context and not isinstance(context['user'], UnauthenticatedUser):
            user: SessionUser = context['user']
            if user.locale:
                try:
                    selected_locale = Locale.parse(user.locale)
                except babel.UnknownLocaleError:
                    pass

        if not selected_locale:
            conn = HTTPConnection(request.scope)
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
        return await call_next(request)

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

