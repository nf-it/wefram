import config
from . import settings, aaa, ui, ds, l10n, mail
from .ui import screens
from .settings.props import NumberProp, NumberMMProp, BooleanProp
from .demo import build as demo
from .const import *


CAPTION = MSG_APP_CAPTION

_CONFIG_REQUIRES = config.DESKTOP['requires']


# Storage
ds.storages.register('users')

# Defining the permissions model
aaa.permissions.register(aaa.PERMISSION_ADMINUSERSROLES, aaa.MSG_PERMISSIONS_USERSROLES)
aaa.permissions.register(aaa.PERMISSION_ADMINSETTINGS, aaa.MSG_PERMISSIONS_SETTINGS)
aaa.permissions.register(mail.PERMISSION, mail.MSG_PERMISSION)
aaa.permissions.register(settings.PERMISSION_ADMINISTERING, settings.PERMISSION_ADMINISTERING_CAPTION)
aaa.permissions.register(settings.PERMISSION_PROPS, settings.PERMISSION_PROPS_CAPTION)

# Defining the settings model
settings.register(
    name='aaa',
    caption=aaa.MSG_APP_CAPTION,
    requires=aaa.PERMISSION_ADMINSETTINGS,
    properties=[
        (aaa.SETTINGS_REMEMBER_USERNAME, BooleanProp(aaa.MSG_SETTINGS_REMEMBER_USERNAME, inline=True)),
        (aaa.SETTINGS_SESSION_LIFETIME, NumberProp(aaa.MSG_SETTINGS_SESSION_LIFETIME)),
        (aaa.SETTINGS_JWT_EXPIRE, NumberProp(aaa.MSG_SETTINGS_JWT_LIFETIME)),
        (aaa.SETTINGS_FAILEDAUTH_DELAY, NumberMMProp(aaa.MSG_SETTINGS_FAILEDAUTH_DELAY, 0, 5, 1)),
        (aaa.SETTINGS_SUCCEEDAUTH_DELAY, NumberMMProp(aaa.MSG_SETTINGS_SUCCEEDAUTH_DELAY, 0, 5, 1)),
    ],
    defaults={
        aaa.SETTINGS_REMEMBER_USERNAME: config.AUTH[aaa.SETTINGS_REMEMBER_USERNAME],
        aaa.SETTINGS_SESSION_LIFETIME: config.AUTH[aaa.SETTINGS_SESSION_LIFETIME],
        aaa.SETTINGS_JWT_EXPIRE: config.AUTH[aaa.SETTINGS_JWT_EXPIRE],
        aaa.SETTINGS_FAILEDAUTH_DELAY: config.AUTH[aaa.SETTINGS_FAILEDAUTH_DELAY],
        aaa.SETTINGS_SUCCEEDAUTH_DELAY: config.AUTH[aaa.SETTINGS_SUCCEEDAUTH_DELAY],
    },
)


# Declaring the default workspace screen
@screens.register(sitemap=-1)
class Desktop(ui.screens.Screen):
    component = 'containers/Desktop'
    icon = ui.media_res_url('icons/workspace.svg')
    caption = l10n.lazy_gettext("Desktop")
    route = '//workspace'
    requires = _CONFIG_REQUIRES

