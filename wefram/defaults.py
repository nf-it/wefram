"""
Provides the platform-level default values for the anything.
"""


CONFIG_DEVEL: bool = True
CONFIG_VERBOSE: bool = False
CONFIG_ECHO_DS: bool = False

UVICORN_LOOP: str = 'uvloop'
UVICORN_BIND: str = '0.0.0.0'
UVICORN_PORT: int = 8000

APP_TITLE: str = "WEFRAM workspace"
PROJECT_NAME: str = "wefram_project"

URL_STATICS: str = '/static'
URL_FILES: str = '/files'
URL_DEFAULT: str = '/welcome'
URL_DEFAULT_AUTHENTICATED: str = '/workspace'
URL_DEFAULT_GUEST: str = '/workspace/login'
URL_ON_LOGOFF: str = '/workspace'
URL_LOGIN_SCREEN: str = '/workspace/login'

AUTH_AUDIENCE: str = 'localhost'
AUTH_JWT_EXPIRE_MINS: int = 0
AUTH_SESSION_TIMEOUT_MINS: int = 720
AUTH_FAILED_AUTH_DELAY: int = 2
AUTH_SUCCEED_AUTH_DELAY: int = 2
AUTH_REMEMBER_USERNAME: bool = True
AUTH_BACKENDS: list = ['local']

DATABASE_USER: str = 'projectdba'
DATABASE_PASS: str = 'project'
DATABASE_NAME: str = 'project'
DATABASE_HOST: str = '127.0.0.1'
DATABASE_PORT: int = 5432
DATABASE_MIGRATE_DROP_MISSING_TABLES: bool = False
DATABASE_MIGRATE_DROP_MISSING_COLUMNS: bool = False

STORAGE_ROOT: str = '.storage'
STORAGE_FILES_DIR: str = 'files'

REDIS_URI: str = 'redis://localhost/0'
REDIS_PASSWORD: (str, None) = None

DEFAULT_LOCALE: str = 'en_US'

BUILD_DIR: str = '.build'
ASSETS_SOURCE: str = 'assets'
FRONTEND_COMPONENTS_PROJECTLAYOUT: str = 'system/containers/Layout'
FRONTEND_COMPONENTS_PROJECTSIDEBAR: str = 'system/containers/LayoutSidebar'
FRONTEND_COMPONENTS_PROJECTSCREENS: str = 'system/containers/LayoutScreens'
FRONTEND_THEME: str = 'system/project/theme'
DEPLOY_PATH: str = '.deploy'
DEPLOY_CLEAN: bool = False
DEPLOY_STATICS: str = '.static'
DEPLOY_ASSETS: str = '.assets'
