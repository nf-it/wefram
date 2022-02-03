"""
Provides the project static configuration.

Do NOT modify this file, use environment variables or `config.json` file instead.
The environment values will have the higher priority than same taken from the
``config.json`` JSON file.
"""

from typing import *
import os
import os.path
import json
import wefram
import wefram.confskel as skeletons
import wefram.defaults as defaults


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
        # If the name consists of dot ('.') in the name (for example: 'scope.name'), then
        # the first part will be used as a scope name, and the last of the name will be used
        # as a value name.
        names: List[str] = name.split('.', 1)
        scope: Optional[str] = names[0] if len(names) == 2 else None
        param: str = names[-1]

        # Making the corresponding environment option name to try to search for the
        # value in the environment.
        envname: str = '_'.join([str(s).upper() for s in (scope or 'PROJECT', param) if s])
        envval: Optional[str] = os.environ.get(envname, None)
        if envval is not None:
            return envval

        # We will try to find the requested value over actual (current) and over
        # default (if exists) configurations.
        _configs: list = [PROJECT_CONFIG, PROJECT_CONFIG_DEFAULT]

        for _config in _configs:
            if not _config:  # If the config did not loaded - skipping it (of cource)
                continue
            if scope:
                if scope not in _config:
                    continue
                return _config[scope].get(param, default)
            elif param in _config:
                return _config.get(param, default)

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


PRJ_ROOT: str = os.getcwd()


PROJECT_CONFIG: Any = None
PROJECT_CONFIG_DEFAULT: Any = None

# Loading the actual (deployed) config
if os.path.isfile(os.path.join(PRJ_ROOT, 'config.json')):
    with open(os.path.join(PRJ_ROOT, 'config.json')) as f:
        PROJECT_CONFIG = json.load(f)

# Loading the default (usually saved in the repo) config
if os.path.isfile(os.path.join(PRJ_ROOT, 'config.default.json')):
    with open(os.path.join(PRJ_ROOT, 'config.default.json')) as f:
        PROJECT_CONFIG_DEFAULT = json.load(f)

# --
# -- Custom configuration
# --


PROJECT: dict = read('project', None) or {}


# --
# -- The runtime and production configuration
# --

PRODUCTION: bool = not read('devel', defaults.CONFIG_DEVEL, 'bool')
VERBOSE: [str, int, bool] = read('verbose', defaults.CONFIG_VERBOSE, 'bool')
ECHO_DS: bool = read('echo_ds', defaults.CONFIG_ECHO_DS, 'bool')

UVICORN_LOOP: str = read('uvicorn.loop', defaults.UVICORN_LOOP, 'str')
UVICORN_BIND: str = read('uvicorn.bind', defaults.UVICORN_BIND, 'str')
UVICORN_PORT: int = read('uvicorn.port', defaults.UVICORN_PORT, 'int')


# --
# -- The project configuration
# --

APP_TITLE: str = read('appTitle', defaults.APP_TITLE, 'str')
PROJECT_NAME: str = read('projectName', defaults.PROJECT_NAME, 'str')
URL: dict = {
    'statics': defaults.URL_STATICS,
    'files': defaults.URL_FILES,
    'default': read('url.default', defaults.URL_DEFAULT, 'str'),
    'default_authenticated': read('url.defaultAuthenticated', defaults.URL_DEFAULT_AUTHENTICATED, 'str'),
    'default_guest': read('url.defaultGuest', defaults.URL_DEFAULT_GUEST, 'str'),
    'on_logoff': read('url.onLogoff', defaults.URL_ON_LOGOFF, 'str'),
    'login_screen': read('url.loginScreen', defaults.URL_LOGIN_SCREEN, 'str')
}
AUTH: dict = {
    'salt': read('auth.salt', "--PLEASE-CHANGE-THIS-TO-THE-RANDOM--", 'str'),
    'secret': read('auth.secret', "--PLEASE-CHANGE-THIS-TO-THE-RANDOM--", 'str'),
    'audience': read('auth.audience', defaults.AUTH_AUDIENCE, 'str'),
    'jwt_expire_mins': read('auth.jwtExpireMins', defaults.AUTH_JWT_EXPIRE_MINS, 'int'),
    'session_timeout_mins': read('auth.sessionTimeoutMins', defaults.AUTH_SESSION_TIMEOUT_MINS, 'int'),
    'failed_auth_delay': read('auth.failedAuthDelay', defaults.AUTH_FAILED_AUTH_DELAY, 'int'),
    'succeed_auth_delay': read('auth.succeedAuthDelay', defaults.AUTH_SUCCEED_AUTH_DELAY, 'int'),
    'remember_username': read('auth.rememberUsername', defaults.AUTH_REMEMBER_USERNAME, 'bool'),
    'backends': read('auth.backends') or defaults.AUTH_BACKENDS
}
DATABASE: dict = {
    'user': read('db.user', defaults.DATABASE_USER, 'str'),
    'pass': read('db.pass', defaults.DATABASE_PASS, 'str'),
    'host': read('db.host', defaults.DATABASE_HOST, 'str'),
    'port': read('db.port', defaults.DATABASE_PORT, 'int'),
    'name': read('db.name', defaults.DATABASE_NAME, 'str'),
    'migrate': {
        'drop_missing_tables': read('db.migrate.dropMissingTables', defaults.DATABASE_MIGRATE_DROP_MISSING_TABLES, 'bool'),
        'drop_missing_columns': read('db.migrate.dropMissingColumns', defaults.DATABASE_MIGRATE_DROP_MISSING_COLUMNS, 'bool')
    }
}
STORAGE: dict = {
    'root': read('storage.root', defaults.STORAGE_ROOT, 'str'),
    'files_dir': read('storage.filesDir', defaults.STORAGE_FILES_DIR, 'str')
}
REDIS: dict = {
    'uri': read('redis.uri', defaults.REDIS_URI, 'str'),
    'password': read('redis.password', defaults.REDIS_PASSWORD) or None
}
SETTINGS_ALWAYS_LOADED: list = read('settings.alwaysLoaded') or []
DEFAULT_LOCALE: str = read('locale.default', defaults.DEFAULT_LOCALE, 'str')
DESKTOP: dict = {
    'requires': read('desktop.requires') or None,
    'intro_text': read('desktop.intro_text') or None
}

STORAGE_DIR: str = STORAGE['root']
STORAGE_ROOT: str = STORAGE_DIR
if STORAGE_ROOT and STORAGE_ROOT.startswith('/') and not os.path.isdir(STORAGE_ROOT):
    # if PRODUCTION:
    #     raise FileNotFoundError(
    #         f"the storage volume's absolute path is invalid: {STORAGE['root']}"
    #     )
    STORAGE_ROOT = os.path.join(PRJ_ROOT, defaults.STORAGE_ROOT)
elif not STORAGE_ROOT:
    STORAGE_ROOT = os.path.join(PRJ_ROOT, defaults.STORAGE_ROOT)
elif STORAGE_ROOT.startswith('./'):
    STORAGE_ROOT = os.path.join(PRJ_ROOT, STORAGE_ROOT[2:])
else:
    STORAGE_ROOT = os.path.join(PRJ_ROOT, STORAGE_ROOT)
FILES_ROOT: str = os.path.join(STORAGE_ROOT, STORAGE['files_dir'])


# --
# -- The build/deployment configuration
# --


if os.path.isfile(os.path.join(PRJ_ROOT, 'build.json')):
    with open(os.path.join(PRJ_ROOT, 'build.json')) as f:
        BUILD_CONF: dict = json.load(f)
elif os.path.isfile(os.path.join(PRJ_ROOT, 'deploy.json')):
    with open(os.path.join(PRJ_ROOT, 'deploy.json')) as f:
        BUILD_CONF: dict = json.load(f)
else:
    BUILD_CONF: dict = skeletons.BUILD_JSON

if os.path.isfile(os.path.join(PRJ_ROOT, 'apps.json')):
    with open(os.path.join(PRJ_ROOT, 'apps.json')) as f:
        APPS_ENABLED: list = json.load(f)
else:
    APPS_ENABLED: list = []


if not BUILD_CONF or not isinstance(BUILD_CONF, dict):
    BUILD_CONF = {}


COREPKG: str = "wefram"  # the Python Wefram package name
CORE_ROOT: str = os.path.split(wefram.__file__)[0]  # The Wefram root path

APPS_ROOT: str = PRJ_ROOT

BUILD_DIR: str = BUILD_CONF.get('buildDir', defaults.BUILD_DIR)
BUILD_ROOT: str = os.path.join(PRJ_ROOT, BUILD_DIR) if not BUILD_DIR.startswith('/') else BUILD_DIR

ASSETS_DIR: str = BUILD_CONF.get('assetsDir', None) or os.path.join(BUILD_DIR, 'assets')
ASSETS_ROOT: str = os.path.join(PRJ_ROOT, ASSETS_DIR) if not ASSETS_DIR.startswith('/') else ASSETS_DIR

ASSETS_SRC_DIR: str = BUILD_CONF.get('assetsSource', None) or None
ASSETS_SRC_ROOT: str = (os.path.join(PRJ_ROOT, ASSETS_SRC_DIR) if not ASSETS_SRC_DIR.startswith('/') else ASSETS_SRC_DIR) if ASSETS_SRC_DIR else None

STATICS_DIR: str = BUILD_CONF.get('staticsDir', None) or os.path.join(BUILD_DIR, 'static')
STATICS_ROOT: str = os.path.join(PRJ_ROOT, STATICS_DIR) if not STATICS_DIR.startswith('/') else STATICS_DIR

DEPLOY: dict = BUILD_CONF.get('deploy', None) or {}
DEPLOY.setdefault('include', [])
DEPLOY.setdefault('exclude', [])
DEPLOY.setdefault('path', defaults.DEPLOY_PATH)
DEPLOY.setdefault('clean', defaults.DEPLOY_CLEAN)
DEPLOY.setdefault('staticsDir', defaults.DEPLOY_STATICS)
DEPLOY.setdefault('assetsDir', defaults.DEPLOY_ASSETS)


# The setting below is only specific for the Wefram development mode when
# the core is in the development environment itself. Not usable for the
# any Wefram-based project because is used for the internal procedures
# and testing environment of the framework itself only.

WEFRAM_MASTER_DEVELOPMENT: bool = read('development.weframMasterDevelopment', False, 'bool')
