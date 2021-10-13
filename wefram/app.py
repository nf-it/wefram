from . import config, ds, aaa, settings
from .settings.props import NumberProp, NumberMMProp, BooleanProp
from .private import const
from .l10n import lazy_gettext
# from .demo import build as demo


CAPTION = lazy_gettext("System")

_CONFIG_REQUIRES = config.DESKTOP['requires']


# Storage
ds.storages.register('users')

# Defining the permissions model
aaa.permissions.register(const.aaa.PERMISSION_ADMINUSERSROLES, const.aaa.MSG_PERMISSIONS_USERSROLES)
aaa.permissions.register(const.aaa.PERMISSION_ADMINSETTINGS, const.aaa.MSG_PERMISSIONS_SETTINGS)
aaa.permissions.register(const.mail.PERMISSION, const.mail.MSG_PERMISSION)
aaa.permissions.register(const.settings.PERMISSION_ADMINISTERING, const.settings.PERMISSION_ADMINISTERING_CAPTION)
aaa.permissions.register(const.settings.PERMISSION_PROPS, const.settings.PERMISSION_PROPS_CAPTION)

# Defining the settings model
settings.register(
    name='aaa',
    caption=const.aaa.MSG_APP_CAPTION,
    requires=const.aaa.PERMISSION_ADMINSETTINGS,
    properties=[
        (const.aaa.SETTINGS_REMEMBER_USERNAME, BooleanProp(const.aaa.MSG_SETTINGS_REMEMBER_USERNAME, inline=True)),
        (const.aaa.SETTINGS_SESSION_LIFETIME, NumberProp(const.aaa.MSG_SETTINGS_SESSION_LIFETIME)),
        (const.aaa.SETTINGS_JWT_EXPIRE, NumberProp(const.aaa.MSG_SETTINGS_JWT_LIFETIME)),
        (const.aaa.SETTINGS_FAILEDAUTH_DELAY, NumberMMProp(const.aaa.MSG_SETTINGS_FAILEDAUTH_DELAY, 0, 5, 1)),
        (const.aaa.SETTINGS_SUCCEEDAUTH_DELAY, NumberMMProp(const.aaa.MSG_SETTINGS_SUCCEEDAUTH_DELAY, 0, 5, 1)),
    ],
    defaults={
        const.aaa.SETTINGS_REMEMBER_USERNAME: config.AUTH[const.aaa.SETTINGS_REMEMBER_USERNAME],
        const.aaa.SETTINGS_SESSION_LIFETIME: config.AUTH[const.aaa.SETTINGS_SESSION_LIFETIME],
        const.aaa.SETTINGS_JWT_EXPIRE: config.AUTH[const.aaa.SETTINGS_JWT_EXPIRE],
        const.aaa.SETTINGS_FAILEDAUTH_DELAY: config.AUTH[const.aaa.SETTINGS_FAILEDAUTH_DELAY],
        const.aaa.SETTINGS_SUCCEEDAUTH_DELAY: config.AUTH[const.aaa.SETTINGS_SUCCEEDAUTH_DELAY],
    },
)
