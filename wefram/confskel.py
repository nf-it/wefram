"""
Provides skeletons for the Wefram-based project's configuration
files.
"""

import random
import string


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
    "buildDir": ".build",
    "staticsDir": ".build/static",
    "assetsDir": ".build/assets",
    "assetsSource": "assets",
    "frontend": {
        "components": {
            "ProjectLayout": "system/containers/Layout",
            "ProjectSidebar": "system/containers/LayoutSidebar",
            "ProjectScreens": "system/containers/LayoutScreens"
        },
        "theme": "system/project/theme"
    },
    "deploy": {
        "include": [],
        "exclude": [],
        "path": ".deploy",
        "clean": False,
        "staticsDir": ".static",
        "assetsDir": ".assets"
    }
}

APPS_JSON = []

CONFIG_JSON = {
    "project": {},
    "projectName": "wefram_based_project",
    "appTitle": "Wefram Workspace",
    "auth": {
        "salt": random_secret(64),
        "secret": random_secret(64),
        "sessionTimeoutMins": 720,
        "rememberUsername": True,
        "backends": ['local'],
    },
    "url": {
        # "statics": "/static",
        # "files": "/files",
        "default": "/workspace",
        "defaultAuthenticated": "/workspace",
        "defaultGuest": "/workspace/login",
        "onLogoff": "/workspace/login",
        "loginScreen": "/workspace/login"
    },
    "db": {
        "user": "wefram",
        "pass": random_secret(64),
        "name": "wefram",
        "port": 5432,
        "migrate.dropMissingTables": True,
        "migrate.dropMissingColumns": True
    },
    "storage": {
        "root": ".storage",
        "filesDir": "files"
    },
    "uvicorn": {
        "port": 8888
    },
    "echo_ds": False,
    "devel": True
}