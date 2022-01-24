from typing import *
from ...models import Session, SettingsCatalog
from ..const.aaa import SETTINGS_REMEMBER_USERNAME
from ... import config, api, l10n, settings, ui
from ...requests import Request, JSONResponse, HTTPException
from ...runtime import context


@api.handle_get('instantiate')
async def instantiate(request: Request) -> JSONResponse:
    """ Responses to the frontend with the current user's environment context, like
    localization parameeters, session information, some configuration etc.
    """

    session: Session = context['session']
    aaa_settings: SettingsCatalog = await settings.get('system.aaa')

    response: dict = {
        'production': config.PRODUCTION,
        'session': session.as_json() if session is not None else None,
        'sidebar': ui.sidebar.as_json(),
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


@api.handle_get('ui/screens/managed/on_render/{name}')
async def render_managed_screen(request: Request) -> JSONResponse:
    """ Used to prepare the managed screen props on the screen render. This
    controller calls from the frontend on every managed screen open and prior
    to that screen been rendered.
    """

    screen_name: str = request.path_params['name']
    screen: ui.screens.ManagedScreen = ui.screens.get_screen_instance(screen_name)

    if screen is None:
        raise HTTPException(404)

    if not hasattr(screen, 'on_render'):
        raise HTTPException(500)

    return JSONResponse(await screen.on_render())
