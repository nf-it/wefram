from ...l10n import lazy_gettext
from ...urls import media_res_url


__all__ = [
    'ICON_USERS',
    'ICON_ROLES',
    'ICON_DOMAINS',

    'MSG_APP_CAPTION',
    'MSG_SETTINGS_REMEMBER_USERNAME',
    'MSG_PERMISSIONS_SETTINGS',
    'MSG_PERMISSIONS_USERSROLES',
    'MSG_PERMISSIONS_TESTING',
    'MSG_SETTINGS_SESSION_LIFETIME',
    'MSG_SETTINGS_JWT_LIFETIME',
    'MSG_SETTINGS_FAILEDAUTH_DELAY',
    'MSG_SETTINGS_SUCCEEDAUTH_DELAY',
    'MSG_USERS',
    'MSG_ROLES',
    'MSG_DOMAINS',

    'PERMISSION_ADMINUSERSROLES',
    'PERMISSION_ADMINSETTINGS',

    'SETTINGS_REMEMBER_USERNAME',
    'SETTINGS_SESSION_LIFETIME',
    'SETTINGS_JWT_EXPIRE',
    'SETTINGS_FAILEDAUTH_DELAY',
    'SETTINGS_SUCCEEDAUTH_DELAY'
]


ICON_USERS = media_res_url('icons/users.png')
ICON_ROLES = media_res_url('icons/roles.png')
ICON_DOMAINS = media_res_url('icons/domains.png'
                             '')

MSG_APP_CAPTION = lazy_gettext("Security", 'system.aaa')
MSG_PERMISSIONS_USERSROLES = lazy_gettext("Administrate users & roles", 'system.aaa')
MSG_PERMISSIONS_SETTINGS = lazy_gettext("Control security settings", 'system.aaa')
MSG_PERMISSIONS_TESTING = lazy_gettext("Running development tests", 'system.aaa')
MSG_SETTINGS_REMEMBER_USERNAME = lazy_gettext("Permit to remember an username at log on screen", 'system.aaa')
MSG_SETTINGS_SESSION_LIFETIME = lazy_gettext("Max session idle time (minutes)", 'system.aaa')
MSG_SETTINGS_JWT_LIFETIME = lazy_gettext("Security token lifetime (minutes)", 'system.aaa')
MSG_SETTINGS_FAILEDAUTH_DELAY = lazy_gettext("Delay when login has failed (secs)", 'system.aaa')
MSG_SETTINGS_SUCCEEDAUTH_DELAY = lazy_gettext("Delay when login has succeed (secs)", 'system.aaa')
MSG_USERS = lazy_gettext("Users", 'system.aaa')
MSG_ROLES = lazy_gettext("Roles", 'system.aaa')
MSG_DOMAINS = lazy_gettext("Active Directory", 'system.aaa')

PERMISSION_ADMINUSERSROLES: str = 'adminUsersRoles'
PERMISSION_ADMINSETTINGS: str = 'adminSettings'

SETTINGS_REMEMBER_USERNAME: str = 'remember_username'
SETTINGS_SESSION_LIFETIME: str = 'session_timeout_mins'
SETTINGS_JWT_EXPIRE: str = 'jwt_expire_mins'
SETTINGS_FAILEDAUTH_DELAY: str = 'failed_auth_delay'
SETTINGS_SUCCEEDAUTH_DELAY: str = 'succeed_auth_delay'
