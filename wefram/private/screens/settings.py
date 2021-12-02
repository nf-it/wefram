from ... import ui
from ..const.settings import (
    APP_ID,
    APP_ICON,
    SITEMAP_CAPTION,
    PROPS_CAPTION,
    PROPS_ICON,
    PERMISSION_ADMINISTERING,
    PERMISSION_PROPS
)
from ..const import aaa, mail


__all__ = [
    'SettingsScreen',
    'UsersScreen',
    'RolesScreen',
    'RoleScreen',
    'AuthBackendAdDomainsScreen'
]


SITEMAP_FOLDER_ID: str = APP_ID

ui.sitemap.append(
    SITEMAP_FOLDER_ID,
    SITEMAP_CAPTION,
    icon=APP_ICON,
    requires=PERMISSION_ADMINISTERING,
    order=99999
)


@ui.screens.register(sitemap=SITEMAP_FOLDER_ID)
class SettingsScreen(ui.screens.Screen):
    component = 'containers/SettingsScreen'
    route = '/properties'
    parent = APP_ID
    icon = PROPS_ICON
    requires = PERMISSION_PROPS
    caption = PROPS_CAPTION
    order = 10


@ui.screens.register(sitemap=SITEMAP_FOLDER_ID)
class UsersScreen(ui.screens.Screen):
    component = 'containers/Users'
    route = '/users'
    parent = APP_ID
    icon = aaa.ICON_USERS
    requires = aaa.PERMISSION_ADMINUSERSROLES
    caption = aaa.MSG_USERS
    order = 20


@ui.screens.register(sitemap=SITEMAP_FOLDER_ID)
class RolesScreen(ui.screens.Screen):
    component = 'containers/Roles'
    route = '/roles'
    parent = APP_ID
    icon = aaa.ICON_ROLES
    requires = aaa.PERMISSION_ADMINUSERSROLES
    caption = aaa.MSG_ROLES
    order = 30


@ui.screens.register
class RoleScreen(ui.screens.Screen):
    component = 'containers/Role'
    parent = APP_ID
    route = '/roles/{key}'
    requires = aaa.PERMISSION_ADMINUSERSROLES


@ui.screens.register(sitemap=SITEMAP_FOLDER_ID)
class AuthBackendAdDomainsScreen(ui.screens.Screen):
    component = 'containers/AuthBackendAdDomains'
    route = '/auth/domains'
    parent = APP_ID
    icon = aaa.ICON_DOMAINS
    requires = aaa.PERMISSION_ADMINUSERSROLES
    caption = aaa.MSG_DOMAINS
    order = 40


@ui.screens.register(sitemap=SITEMAP_FOLDER_ID)
class MailAccountsScreen(ui.screens.Screen):
    component = 'containers/MailAccounts'
    route = '/mail/accounts'
    parent = APP_ID
    icon = mail.APP_ICON
    requires = mail.PERMISSION
    caption = mail.MSG_APP_CAPTION
    order = 50
