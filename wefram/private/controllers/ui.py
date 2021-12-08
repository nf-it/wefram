from typing import *
from ...models import Session, SettingsCatalog
from ..const.aaa import SETTINGS_REMEMBER_USERNAME
from ... import config, api, l10n, settings, ui
from ...requests import Request, JSONResponse
from ...runtime import context


@api.handle_get('instantiate')
async def instantiate(request: Request) -> JSONResponse:
    session: Session = context['session']
    aaa_settings: SettingsCatalog = await settings.get('system.aaa')

    response: dict = {
        'production': config.PRODUCTION,
        'session': session.as_json() if session is not None else None,
        'sitemap': ui.sitemap.as_json(),
        'screens': ui.screens.runtime_json(),
        'locale': l10n.ui_locale_json(),
        'title': config.APP_TITLE,
        'localization': l10n.pack_dictionary(),
        'urlConfiguration': {
            'loginScreenUrl': config.URL['login_screen'],
            'defaultAuthenticatedUrl': config.URL['default_authenticated'] or config.URL['default'],
            'defaultGuestUrl': config.URL['default_guest'] or config.URL['default'],
            'onLogoffUrl': config.URL['on_logoff'] or config.URL['default_guest'] or config.URL['default']
        },
        'aaaConfiguration': {
            'rememberUsername': bool(aaa_settings[SETTINGS_REMEMBER_USERNAME])
        }
    }
    return JSONResponse(response)
