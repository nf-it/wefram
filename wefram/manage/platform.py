""" The Wefram specific internal management on the platform development level """

from typing import *
import subprocess
import aiohttp
import os.path
import shutil
import datetime
import json
import tarfile
from ..tools import CSTYLE
from .. import config
from . import make


__all__ = [
    'upgrade_system',
    'run'
]


DOCS_BUILD = os.path.join(config.CORE_ROOT, 'docs', 'build', 'html')
DOCS_ROOT = os.path.join(config.PRJ_ROOT, 'docs')

API_RELEASES_URL = "https://api.github.com/repos/nf-it/wefram/releases"
REPO_ROOT = os.path.join(config.PRJ_ROOT, '.repos')


def system_release_tarball(version: str) -> str:
    return f"system--{version}.tgz"


def get_system_version() -> Optional[str]:
    version_fn: str = os.path.join(config.PRJ_ROOT, '.version')
    if not os.path.isfile(version_fn):
        return None
    with open(version_fn, 'r') as f:
        return str(f.read()).strip() or None


async def download_release(url: str, version: str) -> bool:
    release_fn: str = os.path.join(REPO_ROOT, system_release_tarball(version))
    if os.path.isfile(release_fn):
        os.unlink(release_fn)
    print(f"Downloading release from [github] repository: {version}")

    with open(release_fn, 'wb') as tarball:
        async with aiohttp.ClientSession() as httpreq:
            async with httpreq.get(url) as response:
                if response.status != 200:
                    return False
                async for data, _ in response.content.iter_chunks():
                    print('.', end='', flush=True)
                    tarball.write(data)
                print("\ndone")
    return True


async def ensure_release(url: str, version: str) -> None:
    release_fn: str = os.path.join(REPO_ROOT, system_release_tarball(version))
    if os.path.isfile(release_fn):
        print(f"Found cached release: {version}")
        return
    print(f"Not found cached release, about to be downloaded: {version}")
    await download_release(url, version)


async def get_latest_version(pre_release: bool = False) -> dict:
    async with aiohttp.ClientSession() as httpreq:
        async with httpreq.get(
                API_RELEASES_URL if pre_release else '/'.join([API_RELEASES_URL, 'latest'])
        ) as response:
            if response.status != 200:
                raise RuntimeError(
                    "failed to fetch release list"
                )

            if pre_release:
                releases: list = sorted(
                    json.loads(await response.text()),
                    key=lambda release: datetime.datetime.fromisoformat(release['published_at'].replace('Z', ''))
                )
                return releases[-1]
            else:
                return json.loads(await response.text())


async def extract_release(version: str) -> None:
    release_fn: str = os.path.join(REPO_ROOT, system_release_tarball(version))
    releases_path: str = os.path.join(REPO_ROOT, 'system')
    if os.path.isdir(os.path.join(REPO_ROOT, 'system', version)):
        shutil.rmtree(os.path.join(REPO_ROOT, 'system', version))
    if not os.path.isfile(release_fn):
        raise FileNotFoundError(release_fn)
    with tarfile.open(release_fn, 'r') as archive:
        members: List[tarfile.TarInfo] = archive.getmembers()
        release_pakdirname: str = (members[0].name.split('/'))[0]
        archive.extractall(releases_path)
    os.rename(
        os.path.join(releases_path, release_pakdirname),
        os.path.join(releases_path, version)
    )


async def install_system_release(version: str) -> None:
    release_path: str = os.path.join(REPO_ROOT, 'system', version)
    if not os.path.exists(release_path):
        raise FileNotFoundError(release_path)
    if not os.path.isdir(release_path):
        raise NotADirectoryError(release_path)
    print("deploying the platform files")
    shutil.rmtree(config.CORE_ROOT)
    shutil.copytree(os.path.join(release_path, 'wefram'), config.CORE_ROOT)


def write_system_version(version: str) -> None:
    version_fn: str = os.path.join(config.PRJ_ROOT, '.version')
    with open(version_fn, 'w') as f:
        f.write(version)


async def after_system_upgraded() -> None:
    await make.run(['all'])


async def upgrade_system(pre_release: bool) -> bool:
    release: dict = await get_latest_version(pre_release)
    if not release:
        print(
            f"{CSTYLE['yellow']}[ SKIP ]{CSTYLE['clear']} there are no releases available"
        )
        return False
    current_version: str = get_system_version()
    release_version: str = release['tag_name']
    if current_version == release_version:
        print(
            f"{CSTYLE['green']}[ SKIP ]{CSTYLE['clear']} current system version is already the latest one"
        )
        return False
    print(f"Current version: {current_version}")
    print(f"Available version: {release_version}")

    os.makedirs(REPO_ROOT, exist_ok=True)
    await ensure_release(release['tarball_url'], release_version)
    await extract_release(release_version)
    await install_system_release(release_version)
    await after_system_upgraded()
    write_system_version(release_version)


def makedocs() -> None:
    os.chdir(os.path.join(config.CORE_ROOT, 'docs'))
    subprocess.run(['make', 'clean'])
    subprocess.run(['make', 'html'])

    # some post-processing correcting mistakes of sphinx
    with open(os.path.join(DOCS_BUILD, 'ds', 'orm.html'), 'r') as f:
        s = f.read()
    with open(os.path.join(DOCS_BUILD, 'ds', 'orm.html'), 'w') as f:
        f.write(s
                .replace('system.ds.model.', 'ds.')
                .replace('system.ds.orm.model.', 'ds.')
                )
    with open(os.path.join(DOCS_BUILD, 'ds', 'models.html'), 'r') as f:
        s = f.read()
    with open(os.path.join(DOCS_BUILD, 'ds', 'models.html'), 'w') as f:
        f.write(s
                .replace('system.ds.model.', 'ds.')
                .replace('system.ds.orm.model.', 'ds.')
                )

    # copying the docs contents into the root
    shutil.rmtree(os.path.join(config.PRJ_ROOT, 'docs'), ignore_errors=True)
    shutil.copytree(
        os.path.join(DOCS_BUILD),
        os.path.join(DOCS_ROOT)
    )


def make_nodejs() -> None:
    from .targets import webpack
    webpack.run()


async def run(params: List[str]) -> None:
    if not params:
        return

    command = params.pop(0)
    if command == 'makedocs':
        makedocs()
        print("done")
        return

    elif command == 'node':
        make_nodejs()
        print("done")
        return

    print(f"Unknown platform command: {command}")

