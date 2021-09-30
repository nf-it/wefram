""" .. Project static configuration

Do NOT modify this file, use environment variables or `config.json` file instead.
The environment values will have the higher priority than same taken from the
`config.json` JSON file.

"""

from typing import *
import os
import json


__version__ = 1


def read(
        name: str,
        default: Any = None,
        valtype: Literal['str', 'bool', 'int', 'float', 'any'] = 'any'
) -> Any:
    """ Returns the value from environment vars or from `config.json` if any, or default
    value otherwise.

    :param name: The name of the corresponding parameter
    :type name: str

    :param default: The default value of the corresponding parameter
    :type default: Any

    :param valtype: The required type of the configuration value
    :type valtype: one of: 'str' | 'bool' | 'int' | 'float' | 'any'

    :return: The value from the ENV or from JSON or default one

    """

    def _get_plain_value() -> Any:
        names: List[str] = name.split('.', 1)
        scope: Optional[str] = names[0] if len(names) == 2 else None
        param: str = names[-1]

        envname: str = '_'.join([str(s).upper() for s in (scope or 'PROJECT', param) if s])
        envval: Optional[str] = os.environ.get(envname, None)
        if envval is not None:
            return envval

        if _json_config:
            if scope:
                if scope not in _json_config:
                    return default
                return _json_config[scope].get(param, default)
            else:
                return _json_config.get(param, default)

        return default

    value: Any = _get_plain_value()
    if value is ...:
        raise ValueError(
            f"configuration error: '{name}' value is required to be configured for the project!"
        )

    if valtype == 'bool':
        if isinstance(value, (bool, int, float)):
            return bool(value)
        if isinstance(value, str):
            value: str = value.lower()
            return value.startswith('t') or value.startswith('y') or value == '1'
        return False

    elif valtype == 'int':
        try:
            return int(value)
        except ValueError:
            return default

    elif valtype == 'float':
        try:
            return float(value)
        except ValueError:
            return default

    elif valtype == 'str':
        return str(value)

    return value


_json_config: Any = None
if os.path.isfile('./config.json'):
    with open('./config.json') as f:
        _json_config = json.load(f)

# --
# -- Custom configuration
# --


PROJECT: dict = read('project', None) or {}


# --
# -- The runtime and production configuration
# --

PRODUCTION: bool = not read('devel', False, 'bool')
VERBOSE: [str, int, bool] = read('verbose', False, 'bool')
ECHO_DS: bool = read('echo_ds', False, 'bool')

UVICORN_LOOP: str = read('uvicorn.loop', 'uvloop', 'str')
UVICORN_BIND: str = read('uvicorn.bind', '0.0.0.0', 'str')
UVICORN_PORT: int = read('uvicorn.port', 8000, 'int')


# --
# -- The project configuration
# --

APP_TITLE: str = read('appTitle', "WEFRAM workspace", 'str')
URL: dict = {
    'default': read('url.default', '/welcome', 'str'),
    'default_authenticated': read('url.defaultAuthenticated', '/workspace', 'str'),
    'default_guest': read('url.defaultGuest', '/welcome', 'str'),
    'on_logoff': read('url.onLogoff', '/workspace', 'str'),
    'login_screen': read('url.loginScreen', '/workspace/login', 'str')
}
AUTH: dict = {
    'salt': read('auth.salt', ..., 'str'),
    'secret': read('auth.secret', ..., 'str'),
    'audience': read('auth.audience', 'localhost', 'str'),
    'jwt_expire_mins': read('auth.jwtExpireMins', 0, 'int'),
    'session_timeout_mins': read('auth.sessionTimeoutMins', 720, 'int'),
    'failed_auth_delay': read('auth.failedAuthDelay', 2, 'int'),
    'succeed_auth_delay': read('auth.succeedAuthDelay', 2, 'int'),
    'remember_username': read('auth.rememberUsername', True, 'bool'),
    'backends': read('auth.backends') or ['local']
}
DATABASE: dict = {
    'user': read('db.user', ..., 'str'),
    'pass': read('db.pass', ..., 'str'),
    'host': read('db.host', '127.0.0.1', 'str'),
    'port': read('db.port', 5432, 'int'),
    'name': read('db.name', ..., 'str'),
    'migrate': {
        'drop_missing_tables': read('db.migrate.dropMissingTables', False, 'bool'),
        'drop_missing_columns': read('db.migrate.dropMissingColumns', False, 'bool')
    }
}
REDIS: dict = {
    'uri': read('redis.uri', 'redis://localhost/0', 'str'),
    'password': read('redis.password', None) or None
}
SETTINGS_ALWAYS_LOADED: list = read('settings.alwaysLoaded') or []
DEFAULT_LOCALE: str = read('locale.default', 'en_US', 'str')
DESKTOP: dict =  {
    'requires': read('desktop.requires') or None
}


# --
# -- The build and global system configuration
# --

with open('./build.json') as f:
    _BUILD_CONF: dict = json.load(f)

with open('./apps.json') as f:
    APPS_ENABLED: list = json.load(f)

COREDIR: str = _BUILD_CONF['coreDir']
APPSDIR: str = _BUILD_CONF['appsDir']
BUILDDIR: str = _BUILD_CONF['buildDir']
PRJROOT: str = os.path.abspath(os.path.dirname(__file__))
COREROOT: str = os.path.join(PRJROOT, COREDIR)
APPSROOT: str = os.path.join(PRJROOT, APPSDIR)
BUILDROOT: str = os.path.join(PRJROOT, BUILDDIR)

ASSETS_DIR: str = _BUILD_CONF['assetsDir'] or None
ASSETS_ROOT: str = os.path.join(PRJROOT, ASSETS_DIR) if ASSETS_DIR else None
STATICS_ROOT: str = os.path.join(PRJROOT, _BUILD_CONF['staticsDir'])
STATICS_URL: str = _BUILD_CONF['staticsUrl']
FILES_DIR: str = _BUILD_CONF['filesDir']
FILES_ROOT: str = os.path.join(PRJROOT, FILES_DIR)
FILES_URL: str = _BUILD_CONF['filesUrl']
