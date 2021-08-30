import os
import json


# --
# -- The project configuration
# --

APP_TITLE: str = "WEFRAM workspace"

DEFAULT_URL: str = '/workspace'
DEFAULT_URL_AUTHENTICATED: str = '/workspace'
DEFAULT_URL_GUEST: str = '/workspace'

AUTH: dict = {
    'salt': 'VJJhAVDcf8#gfq8dfguycyaergvC$Tvqwrc8к76свQWuaiudyv$e1!3gh#',
    'secret': '--cFECVWEh0ghgfei78vb7uyVADXHUvu27164&^DF!#$D12/3wqc@*RCGF76f342',
    'audience': 'localhost',
    'jwt_expire_mins': 0,
    'session_timeout_mins': 720,
    'failed_auth_delay': 2,
    'remember_username': True,
    'login_screen_url': '/workspace/login'
}
DATABASE: dict = {
    'user': os.environ.get('DB_USER', 'projectdba'),
    'pass': os.environ.get('DB_PASS', 'YOUR PASSWORD HERE'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 5432) or 5432),
    'name': os.environ.get('DB_NAME', 'project'),
    'migrate': {
        'drop_missing_tables': True,
        'drop_missing_columns': True
    }
}
REDIS: dict = {
    'uri': os.environ.get('REDIS_URI', 'redis://localhost/0'),
    'password': os.environ.get('REDIS_PASSWORD', None)
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
