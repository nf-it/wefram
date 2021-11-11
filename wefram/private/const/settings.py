from ...l10n import lazy_gettext
from ...urls import media_res_url


APP_ICON: str = media_res_url('icons/settings.png')
APP_ID: str = 'settings'
APP_CAPTION = lazy_gettext("Settings & properties", 'system.settings')

SITEMAP_CAPTION = lazy_gettext("Administering", 'system.settings')
PROPS_CAPTION = lazy_gettext("Settings", 'system.settings')
PROPS_ICON = media_res_url('icons/props.png')

PERMISSION_ADMINISTERING_CAPTION = lazy_gettext("Access the administering", 'system.settings')
PERMISSION_PROPS_CAPTION = lazy_gettext("Access properties of the project", 'system.settings')

PERMISSION_ADMINISTERING: str = 'administeringAccess'
PERMISSION_PROPS: str = 'settingsPropertiesAccess'
