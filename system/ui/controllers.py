from typing import *
import config
from .. import api, aaa, l10n, settings
from ..ui import sitemap, screens
from ..requests import Request, JSONResponse, context


class IUrlConfigurationResponse(TypedDict):
    loginScreenUrl: str
    defaultAuthenticatedUrl: str
    defaultGuestUrl: str


class IAaaConfiguration(TypedDict):
    rememberUsername: bool


class IAppInstantiationResponse(TypedDict):
    session: Optional[aaa.ISession]
    sitemap: sitemap.ISitemapResponse
    screens: screens.ScreensRuntime
    title: str
    localization: Dict[str, dict]
    urlConfiguration: IUrlConfigurationResponse
    aaaConfiguration: IAaaConfiguration


@api.handle_get('instantiate')
async def instantiate(request: Request) -> JSONResponse:
    session: aaa.Session = context['session']
    aaa_settings: settings.SettingsCatalog = await settings.get('system.aaa')

    response: IAppInstantiationResponse = {
        'session': session.as_json() if session is not None else None,
        'sitemap': sitemap.as_json(),
        'screens': screens.runtime_json(),
        'title': config.APP_TITLE,
        'localization': l10n.pack_dictionary(),
        'urlConfiguration': {
            'loginScreenUrl': config.AUTH.get('login_screen_url', '/login'),
            'defaultAuthenticatedUrl': getattr(config, 'DEFAULT_URL_AUTHENTICATED', None) or str(config.DEFAULT_URL),
            'defaultGuestUrl': getattr(config, 'DEFAULT_URL_GUEST', None) or str(config.DEFAULT_URL),
        },
        'aaaConfiguration': {
            'rememberUsername': bool(aaa_settings[aaa.SETTINGS_REMEMBER_USERNAME])
        }
    }
    return JSONResponse(response)
