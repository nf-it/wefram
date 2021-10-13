from typing import *
import os
import json
import re
import subprocess
from ... import config
from ...tools import app_root


__all__ = [
    'get_pip_dependencies',
    'get_yarn_dependencies'
]


DEPENDENCIES: dict = {}


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


def dependencies_for(app_name: str) -> Tuple[dict, dict]:
    req_fn: str = os.path.join(app_root(app_name), 'requirements.json')
    if not os.path.isfile(req_fn):
        return {}, {}
    with open(req_fn, 'r') as f:
        req: dict = json.load(f)
        if not isinstance(req, dict) \
                or ('pip' in req and not isinstance(req['pip'], dict)) \
                or ('yarn' in req and not isinstance(req['yarn'], dict)):
            print(
                f"ERROR:: invalid requirements file for '{app_name}' in the '{req_fn}'"
            )
            return {}, {}

        return req.get('pip', {}), req.get('yarn', {})


def collect_dependencies(system_only: bool = False) -> Tuple[dict, dict]:
    all_pip: dict = {}
    all_yarn: dict = {}

    apps: list = [config.COREPKG]
    if not system_only:
        apps.extend(config.APPS_ENABLED)

    for app_name in apps:
        pip, yarn = dependencies_for(app_name)

        for pkg_name, pkg_ver in pip.items():
            all_pip[pkg_name] = fit_dependency_vers(all_pip.get(pkg_name, None), pkg_ver)

        for pkg_name, pkg_ver in yarn.items():
            all_yarn[pkg_name] = fit_dependency_vers(all_yarn.get(pkg_name, None), pkg_ver)

    return all_pip, all_yarn


def collect(system_only: bool = False) -> None:
    pip: dict
    yarn: dict
    pip, yarn = collect_dependencies(system_only)
    DEPENDENCIES['pip'] = pip
    DEPENDENCIES['yarn'] = yarn


def get_pip_dependencies(system_only: bool = False) -> dict:
    if 'pip' in DEPENDENCIES:
        return DEPENDENCIES['pip']
    collect(system_only)
    return DEPENDENCIES['pip']


def get_yarn_dependencies(system_only: bool = False) -> dict:
    if 'yarn' in DEPENDENCIES:
        return DEPENDENCIES['yarn']
    collect(system_only)
    return DEPENDENCIES['yarn']

