import os.path
import subprocess
import json
from ..routines import deps
from ... import config


WEBPACK_CONFIG_PATH: str = os.path.join(config.CORE_ROOT, 'manage', 'dist', 'webpack.config.js')
NODE_MODULES_PATH: str = os.path.join(config.BUILD_ROOT, 'node_modules')
PACKAGE_PATH: str = os.path.join(config.PRJ_ROOT, 'package.json')
TSCONFIG_PATH: str = os.path.join(config.PRJ_ROOT, 'tsconfig.json')
WEFRAM_FRONT_PATH: str = os.path.join(config.CORE_ROOT, 'frontend')


TSCONFIG: dict = {
    "compilerOptions": {
        "allowSyntheticDefaultImports": True,
        "sourceMap": False,
        "target": "es2017",
        "jsx": "react-jsx",
        "module": "esnext",
        "moduleResolution": "node",
        "declaration": False,
        "removeComments": True,
        "esModuleInterop": True,
        "noImplicitReturns": False,
        "noUnusedLocals": False,
        "isolatedModules": True,
        "skipLibCheck": True,
        "strict": True,
        "outDir": "static",
        "lib": [
              "dom",
              "dom.iterable",
              "esnext"
        ],
        "baseUrl": config.PRJ_ROOT,
        "paths": {
            "system/*": [
                os.path.join(config.CORE_ROOT, "frontend/*")
            ],
            "wefram/*": [
                os.path.join(config.CORE_ROOT, "frontend/*")
            ],
            "build/*": [
                os.path.join(config.BUILD_ROOT, "frontend/*")
            ],
            "*": [
                os.path.join(config.PRJ_ROOT, "*")
            ]
        }
    },
    "exclude": [
        "system/frontend/templates",
        "system/skel",
        "wefram/frontend/templates",
        "wefram/skel"
    ]
}


PACKAGE: dict = {
    "name": config.PROJECT_NAME,
    "license": "MIT",
    "scripts": {
        "build": ' '.join([
            f"NODE_ENV=production",
            f"webpack",
            f"--config='{WEBPACK_CONFIG_PATH}'",
            f"--progress",
            f"--mode=production",
            f"--env systempath='{WEFRAM_FRONT_PATH}'"
        ]),
        "build-devel": ' '.join([
            f"NODE_ENV=development",
            f"webpack",
            f"--config='{WEBPACK_CONFIG_PATH}'",
            f"--progress",
            f"--mode=development",
            f"--env systempath='{WEFRAM_FRONT_PATH}'"
        ]),
    },
    "dependencies": {}
}


def run(*_) -> None:
    dependencies: dict = deps.get_yarn_dependencies()

    with open(TSCONFIG_PATH, 'w') as f:
        json.dump(TSCONFIG, f, ensure_ascii=False, indent=2)

    with open(PACKAGE_PATH, 'w') as f:
        package: dict = PACKAGE
        package['dependencies'] = {
            pkg_name: ("latest" if pkg_vers == 'latest' else f"^{pkg_vers}")
            for pkg_name, pkg_vers in dependencies.items()
        }
        json.dump(package, f, ensure_ascii=False, indent=2)

    subprocess.run([
        f'yarn',
        f'install',
    ])
