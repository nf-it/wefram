from typing import *
import os
import json
import re
import subprocess
import config
from .tools import CSTYLE


apps_enabled: List[str] = config.APPS_ENABLED
requirements_pip: Dict[str, Optional[str]] = {}
requirements_yarn: Dict[str, Optional[str]] = {}


def verfrom(verstr: Optional[str]) -> List[int]:
    verints: List[int] = []
    verparts: List[str] = verstr.split('.')
    for p in verparts:
        try:
            verint: int = int(p)
            verints.append(verint)
        except ValueError:
            break
    return verints


def fit_dependency_vers(current: str, requested: str) -> str:
    current = (re.sub('[^.0-9]', '', str(current).lower()) if current is not None else "latest") or "latest"
    requested = (re.sub('[^.0-9]', '', str(requested).lower()) if requested is not None else "latest") or "latest"
    if current == requested or current == "latest":
        return requested
    if requested == "latest":
        return current
    current = verfrom(current)
    requested = verfrom(requested)
    return '.'.join([str(i) for i in max(current, requested)])


def apply_reqs_from(app_dir: str) -> None:
    req_fn: str = os.path.join(config.PRJROOT, app_dir, 'requirements.json')
    if not os.path.isfile(req_fn):
        print(
            f"not collecting requirements from {CSTYLE['red']}{app_dir}{CSTYLE['clear']} - none declared"
        )
        return
    print(
        f"collecting requirements from {CSTYLE['red']}{app_dir}{CSTYLE['clear']}"
    )
    with open(req_fn, 'r') as f:
        req: dict = json.load(f)
        if not isinstance(req, dict) \
                or ('pip' in req and not isinstance(req['pip'], dict)) \
                or ('yarn' in req and not isinstance(req['yarn'], dict)):
            print(
                f"{CSTYLE['red']}[!] invalid requirements file at {app_dir}{CSTYLE['clear']}"
            )
            return

        for pkg_name, pkg_ver in req.get('pip', {}).items():
            requirements_pip[pkg_name] = fit_dependency_vers(requirements_pip.get(pkg_name, None), pkg_ver)

        for pkg_name, pkg_ver in req.get('yarn', {}).items():
            requirements_yarn[pkg_name] = fit_dependency_vers(requirements_pip.get(pkg_name, None), pkg_ver)


async def resolve_deps(with_apps: bool = True) -> None:
    apply_reqs_from('system')
    if with_apps:
        for app_name in apps_enabled:
            apply_reqs_from(os.path.join('project', app_name))

    with open(os.path.join(config.PRJROOT, 'requirements'), 'w') as f:
        f.write('\n'.join([
            pkg_name if pkg_vers == 'latest' else f"{pkg_name}~={pkg_vers}"
            for pkg_name, pkg_vers in requirements_pip.items()
        ]))

    with open(os.path.join(config.PRJROOT, 'package.json'), 'w') as f:
        dependencies: dict = {
            pkg_name: ("latest" if pkg_vers == 'latest' else f"^{pkg_vers}")
            for pkg_name, pkg_vers in requirements_yarn.items()
        }
        package_json: dict = {
            "name": "wefram",
            # "version": "1.0.0",
            "license": "MIT",
            "scripts": {
                "build": "NODE_ENV=production webpack --progress --mode=production",
                "build-devel": "NODE_ENV=development webpack --progress --mode=development"
            },
            "dependencies": dependencies
        }
        json.dump(package_json, f, indent=2)

    print("written resulting dependencies/requirements to the project")
    print(f"running {CSTYLE['yellow']}pip install{CSTYLE['clear']}")
    subprocess.run(['pip', 'install', '--upgrade', 'pip'])
    subprocess.run(['pip', 'install', '-r', 'requirements'])
    print(f"running {CSTYLE['yellow']}yarn install{CSTYLE['clear']}")
    subprocess.run(['yarn', 'install'])


async def execute() -> None:
    await resolve_deps()
    print(f"[v] pre-build {CSTYLE['green']}DONE{CSTYLE['clear']}")
    print(f"running {CSTYLE['yellow']}make{CSTYLE['clear']}")

    from .make import make
    await make()


async def first_install_prepare() -> None:
    await resolve_deps(False)

