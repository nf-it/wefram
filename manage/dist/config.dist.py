import os
import json


# --
# -- The project configuration
# --

APP_TITLE: str = "{{ APP_TITLE }}"

DEFAULT_URL: str = '/workspace'
DEFAULT_URL_AUTHENTICATED: str = '/workspace'
DEFAULT_URL_GUEST: str = '/workspace'

AUTH: dict = {
    'salt': '{{ SALT }}',
    'secret': '{{ SECRET }}',
    'audience': 'localhost',
    'jwt_expire_mins': 0,
    'session_timeout_mins': 720,
    'failed_auth_delay': 2,
    'remember_username': True,
    'login_screen_url': '{{ LOGIN_SCREEN_URL }}'
}
DATABASE: dict = {
    'user': os.environ.get('DB_USER', '{{ DATABASE_USER }}'),
    'pass': os.environ.get('DB_PASS', '{{ DATABASE_PASSWORD }}'),
    'host': os.environ.get('DB_HOST', '{{ DATABASE_HOST }}'),
    'port': int(os.environ.get('DB_PORT', 5432) or 5432),
    'name': os.environ.get('DB_NAME', '{{ DATABASE_NAME }}')
}
REDIS: dict = {
    'uri': os.environ.get('REDIS_URI', 'redis://localhost/{{ REDIS_DBNUM }}'),
    'password': os.environ.get('REDIS_PASSWORD', '{{ REDIS_PASSWORD }}' or None)
}
SETTINGS_ALWAYS_LOADED: list = [

]
DEFAULT_LOCALE: str = 'en_US'
WORKSPACE: dict = {
    'requires': None
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
PRJROOT: str = os.path.abspath(os.path.dirname(__file__))
COREROOT: str = os.path.join(PRJROOT, COREDIR)
APPSROOT: str = os.path.join(PRJROOT, APPSDIR)

PRODUCTION: bool = not os.environ.get('DEVEL', 'false').lower().startswith('t')
VERBOSE: [str, int, bool] = os.environ.get('VERBOSE', False)

UVICORN_LOOP: str = 'uvloop'
UVICORN_BIND: str = '0.0.0.0'
UVICORN_PORT: int = 8000

ASSETS_DIR: str = _BUILD_CONF['assetsDir'] or None
ASSETS_ROOT: str = os.path.join(PRJROOT, ASSETS_DIR) if ASSETS_DIR else None
STATICS_ROOT: str = os.path.join(PRJROOT, _BUILD_CONF['staticsDir'])
STATICS_URL: str = _BUILD_CONF['staticsUrl']
FILES_DIR: str = _BUILD_CONF['filesDir']
FILES_ROOT: str = os.path.join(PRJROOT, FILES_DIR)
FILES_URL: str = _BUILD_CONF['filesUrl']
