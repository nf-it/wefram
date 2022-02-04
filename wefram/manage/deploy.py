"""
Provides the facility to deploy the project from the management/
development layer to the production one.

This procedure prepares the neccessary deployment configurations
like *Dockerfile* and *requirements*, and copies enabled (and only
enabled) applications and system files to the deployment
target path.

Optionally, basing on the 'clean' configuration parameter, this
facility may remove all existing files from the deployment
target directory, excluding only directory used for storages
(if that directory is located in the deployment directory).
"""

from typing import *
import os
import os.path
import shutil
import subprocess
import json
from distutils.dir_util import copy_tree
from .. import config, logger, defaults, confskel
from .routines.tools import yesno, json_to_file, merge_conf
from .routines.project import make_deploying_srcs
from . import make


DEPLOYMENT_ROOT: str = os.path.join(config.PRJ_ROOT, config.DEPLOY['path']) \
        if not config.DEPLOY['path'].startswith('/') \
        else config.DEPLOY['path']

SOURCES: List[str] = make_deploying_srcs()

STATICS_DST: str = config.DEPLOY['staticsDir'] \
    if config.DEPLOY['staticsDir'].startswith('/') \
    else os.path.join(DEPLOYMENT_ROOT, config.DEPLOY['staticsDir'])

ASSETS_DST: str = config.DEPLOY['assetsDir'] \
    if config.DEPLOY['assetsDir'].startswith('/') \
    else os.path.join(DEPLOYMENT_ROOT, config.DEPLOY['assetsDir'])


def clean(full: bool = False) -> None:
    """ Cleans up the deployment destination directory from the existing
    files and directories. If the ``full`` parameter is set to ``True`` - all
    existing files, even not included in the deployment sources, will be
    removed. Otherwise, only conflicting rooted files will be removed, keeping
    all other ones whose are not included in the deployment list.

    Note that if the *storage* directory is located in the deployment directory
    (for example, if the deplotment location is used as the production
    environment directly) - it will NOT be removed to avoid loosing of data.

    Note that to simplicity the project's deployment using a version control
    system - the '.git' directory is excluded too, even if present in the
    deployment directory.

    Note that most popular to use virtualenv directories' names like
    'venv' and '.venv' will be excluded too.

    :param full:
        If set to ``True`` - all files except the *storage* directory will be
        removed from the deployment root; otherwise only conflicting (deploying)
        ones will be.
    """

    exclude: List[str] = [
        '.git',
        '.venv',
        'venv',
        'config.json',
    ]  # The list of excluded from the cleanup roots

    storage_dir: str = config.STORAGE_DIR or defaults.STORAGE_ROOT
    if storage_dir and not storage_dir.startswith('/'):
        exclude.append(storage_dir.split('/')[0])

    cleanup: List[str] = [
        src for src in
        (SOURCES if not full else os.listdir(DEPLOYMENT_ROOT))
        if src not in exclude
    ]
    print("Cleaning up deployment directory:", DEPLOYMENT_ROOT)

    for f in cleanup:
        fq: str = os.path.join(DEPLOYMENT_ROOT, f)
        if not os.path.exists(fq):
            continue
        print(f".. removing existing: {f}")
        if os.path.isdir(fq):
            shutil.rmtree(fq)
        else:
            os.unlink(fq)

    print(f"Cleaning up statics directory: {STATICS_DST}")
    if os.path.exists(STATICS_DST):
        shutil.rmtree(STATICS_DST)

    print(f"Cleaning up assets directory: {ASSETS_DST}")
    if os.path.exists(ASSETS_DST):
        shutil.rmtree(ASSETS_DST)


def make_deploy_json() -> None:
    """ Generates the ``deploy.json`` file and stores it to the deployment
    directory. This file is used instead of the ``build.json`` in the
    production environment.
    """

    print("Generating 'deploy.json'")
    json_to_file({
        "staticsDir": config.DEPLOY['staticsDir'],
        "assetsDir": config.DEPLOY['assetsDir']
    }, os.path.join(DEPLOYMENT_ROOT, 'deploy.json'))


def deploy_built() -> None:
    """ Deploys built static files like 'statics' and 'assets'. """

    print("Deploying statics")
    os.makedirs(STATICS_DST, exist_ok=True)
    copy_tree(config.STATICS_ROOT, STATICS_DST)

    print("Deploying assets")
    os.makedirs(ASSETS_DST, exist_ok=True)
    copy_tree(config.ASSETS_ROOT, ASSETS_DST)


def deploy_project() -> None:
    """ Deploys the contents of the project, got by using the function
    :func:`make_deploying_srcs`. Copies both platform specific files
    like 'server.py' and 'asgi.py', and project specific files like
    applications' directories and configurations.
    """

    for e in SOURCES:
        src: str = os.path.join(config.PRJ_ROOT, e)
        dst: str = os.path.join(DEPLOYMENT_ROOT, e)
        if not os.path.exists(src):
            continue
        print("Deploying", e)
        if os.path.isfile(src):
            shutil.copy(src, dst)
        else:
            shutil.copytree(src, dst, ignore=deploy_ignores)


def deploy_ignores(src: str, names: List[str]) -> List[str]:
    if src.endswith('__pycache__'):
        print("INGORE:", src)
        return names
    return [n for n in names if n.endswith('.pyc') or n == '__pycache__']


def make_requirements() -> None:
    """ Generates the 'requirements.txt' file containing the frozen state
    of Python packages list: ``pip freeze > requirements.txt``
    """

    print("Generating requirements registry for Python's `pip install -r`")
    result: subprocess.CompletedProcess = subprocess.run(['pip', 'freeze'], capture_output=True)
    packages: List[str] = [
        s for s in
        result.stdout.decode('utf-8').replace("\\n", "\n").split('\n')
        if s.strip() != '' and not s.strip().startswith('pkg_resources')
    ]

    with open(os.path.join(DEPLOYMENT_ROOT, 'requirements.txt'), 'w') as f:
        f.write('\n'.join(packages))


def prod_config() -> None:
    """ Applies some production configuration options to the deployed
    project's settings, in the 'config.json' and 'config.default.json'.
    """

    project_conf: Any = None
    project_default_conf: Any = None

    # Loading the actual (deployed) config
    if os.path.isfile(os.path.join(DEPLOYMENT_ROOT, 'config.json')):
        with open(os.path.join(DEPLOYMENT_ROOT, 'config.json')) as f:
            project_conf = json.load(f)

    # Loading the default (usually saved in the repo) config
    if os.path.isfile(os.path.join(DEPLOYMENT_ROOT, 'config.default.json')):
        with open(os.path.join(DEPLOYMENT_ROOT, 'config.default.json')) as f:
            project_default_conf = json.load(f)

    # Making the ``/config.default.json``
    print("Updating `config.default.json`")
    project_default_conf = merge_conf(confskel.CONFIG_JSON, project_default_conf or {})
    project_default_conf['devel'] = False
    project_default_conf['echo_ds'] = False
    json_to_file(
        project_default_conf,
        os.path.join(DEPLOYMENT_ROOT, "config.default.json")
    )

    # Making the ``/config.json``. Write this config if is exist in the project only.
    if project_conf:
        print("Updating `config.json`")
        project_conf = merge_conf(confskel.CONFIG_JSON, project_conf or {})
        project_conf['devel'] = False
        project_conf['echo_ds'] = False
        json_to_file(
            project_conf,
            os.path.join(config.PRJ_ROOT, "config.json")
        )
    else:
        print("Skipping `config.json`")


def make_dockerfile() -> None:
    """ Distributes the ``Dockerfile`` in the root path of the deployment.
    Used to build docker container used to deploy this project using
    Docker environment, for example - within AWS or Kubernetes.

    This function also distributes the '.dockerignore' file to avoid
    adding compiled (.pyc), virtualenv (.venv), etc., to the
    builded docker container.
    """

    print("Deploying .dockerignore")
    shutil.copy(
        os.path.join(config.CORE_ROOT, 'manage', 'dist', 'deploy', 'docker', '.dockerignore'),
        os.path.join(DEPLOYMENT_ROOT, '.dockerignore')
    )

    print("Deploying Dockerfile")
    shutil.copy(
        os.path.join(config.CORE_ROOT, 'manage', 'dist', 'deploy', 'docker', 'Dockerfile'),
        os.path.join(DEPLOYMENT_ROOT, 'Dockerfile')
    )


async def run(*_) -> None:
    logger.set_level(logger.WARNING)
    config.PRODUCTION = True

    # Prior to deploy - it is a good idea to execute the 'make all'
    if yesno("Run `make` before deployment?", True):
        await make.run([
            'db',
            'assets',
            'l10n',
            'texts',
            'prefront',
            'react'
        ])
        print("")

    print("Ensuring the deployment directory existance:", DEPLOYMENT_ROOT)
    os.makedirs(DEPLOYMENT_ROOT, exist_ok=True)

    # The clean up of the destination directory
    print("")
    print(
        "The deployment procedure will remove all existing files at the"
        " deployment path, whose conflicting with the deploying sources. This"
        " means that all files and directories at the destination root"
        " directory, whose about to be copied from the source layer, will be"
        " replaced with the deploying ones."
    )
    print(
        "The optional behaviour is what to do with other that specified files"
        " and directories (whose are not conflicting with deploying ones). There"
        " are two options: remove everything (except the 'storage' one) or keep"
        " all existing files whose not about to be replaced with the new ones."
    )
    print("")
    clean_all: bool = yesno(
            "Do full clean up at the deployment directory?\n"
            "WARNING! This will erase ALL data except storage directory!",
            bool(config.DEPLOY['clean'])
    )
    clean(clean_all)

    print("")
    make_deploy_json()

    print("")
    deploy_built()
    deploy_project()

    print("")
    prod_config()

    print("")
    make_requirements()

    print("")
    make_dockerfile()

    print("")
    print("done")
