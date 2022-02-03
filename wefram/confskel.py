"""
Provides skeletons for the Wefram-based project's configuration
files.
"""

import random
import string
from . import defaults


__all__ = [
    'BUILD_JSON',
    'APPS_JSON',
    'CONFIG_JSON'
]


def random_secret(length: int) -> str:
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(length)
    )


BUILD_JSON = {
    "buildDir": defaults.BUILD_DIR,
    "staticsDir": f"{defaults.BUILD_DIR}/static",
    "assetsDir": f"{defaults.BUILD_DIR}/assets",
    "assetsSource": defaults.ASSETS_SOURCE,
    "frontend": {
        "components": {
            "ProjectLayout": defaults.FRONTEND_COMPONENTS_PROJECTLAYOUT,
            "ProjectSidebar": defaults.FRONTEND_COMPONENTS_PROJECTSIDEBAR,
            "ProjectScreens": defaults.FRONTEND_COMPONENTS_PROJECTSCREENS
        },
        "theme": defaults.FRONTEND_THEME
    },
    "deploy": {
        "include": [],
        "exclude": [],
        "path": defaults.DEPLOY_PATH,
        "clean": defaults.DEPLOY_CLEAN,
        "staticsDir": defaults.DEPLOY_STATICS,
        "assetsDir": defaults.DEPLOY_ASSETS
    }
}

APPS_JSON = []

CONFIG_JSON = {
    "project": {},
    "projectName": defaults.PROJECT_NAME,
    "appTitle": defaults.APP_TITLE,
    "auth": {
        "salt": random_secret(64),
        "secret": random_secret(64),
        "audience": defaults.AUTH_AUDIENCE,
        "jwtExpireMins": defaults.AUTH_JWT_EXPIRE_MINS,
        "sessionTimeoutMins": defaults.AUTH_SESSION_TIMEOUT_MINS,
        "rememberUsername": defaults.AUTH_REMEMBER_USERNAME,
        "failedAuthDelay": defaults.AUTH_FAILED_AUTH_DELAY,
        "succeed_auth_delay": defaults.AUTH_SUCCEED_AUTH_DELAY,
        "backends": defaults.AUTH_BACKENDS,
    },
    "url": {
        "default": defaults.URL_DEFAULT,
        "defaultAuthenticated": defaults.URL_DEFAULT_AUTHENTICATED,
        "defaultGuest": defaults.URL_DEFAULT_GUEST,
        "onLogoff": defaults.URL_ON_LOGOFF,
        "loginScreen": defaults.URL_LOGIN_SCREEN
    },
    "db": {
        "user": defaults.DATABASE_USER,
        "pass": random_secret(64),
        "name": defaults.DATABASE_NAME,
        "host": defaults.DATABASE_HOST,
        "port": defaults.DATABASE_PORT,
        "migrate.dropMissingTables": defaults.DATABASE_MIGRATE_DROP_MISSING_TABLES,
        "migrate.dropMissingColumns": defaults.DATABASE_MIGRATE_DROP_MISSING_COLUMNS
    },
    "redis": {
        "uri": defaults.REDIS_URI,
        "password": defaults.REDIS_PASSWORD
    },
    "storage": {
        "root": defaults.STORAGE_ROOT,
        "filesDir": defaults.STORAGE_FILES_DIR
    },
    "uvicorn": {
        "loop": defaults.UVICORN_LOOP,
        "bind": defaults.UVICORN_BIND,
        "port": defaults.UVICORN_PORT
    },
    "settings": {
        "alwaysLoaded": []
    },
    "locale": {
        "default": defaults.DEFAULT_LOCALE
    },
    "desktop": {
        "requires": None,
        "introText": None
    },
    "echo_ds": defaults.CONFIG_ECHO_DS,
    "devel": defaults.CONFIG_DEVEL,
    "verbose": defaults.CONFIG_VERBOSE
}
