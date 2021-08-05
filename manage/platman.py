import asyncio
from typing import *
import sys
import os
import aiohttp
import json
import datetime
import tarfile
import shutil
import config
from .tools import CSTYLE
from . import build


API_RELEASES_URL = "https://api.github.com/repos/nf-it/wefram/releases"
REPO_ROOT = os.path.join(config.PRJROOT, '.repos')


def system_release_tarball(version: str) -> str:
    return f"system--{version}.tgz"


def get_system_version() -> Optional[str]:
    version_fn: str = os.path.join(config.PRJROOT, '.version')
    if not os.path.isfile(version_fn):
        return None
    with open(version_fn, 'r') as f:
        return str(f.read()).strip() or None


async def download_release(url: str, version: str) -> bool:
    release_fn: str = os.path.join(REPO_ROOT, system_release_tarball(version))
    if os.path.isfile(release_fn):
        os.unlink(release_fn)
    print(f"Downloading release from [github] repository: {version}")

    loop = asyncio.get_event_loop()
    term_reader = asyncio.StreamReader()
    w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    term_stdout = asyncio.StreamWriter(w_transport, w_protocol, term_reader, loop)

    with open(release_fn, 'wb') as tarball:
        async with aiohttp.ClientSession() as httpreq:
            async with httpreq.get(url) as response:
                if response.status != 200:
                    return False
                async for data, _ in response.content.iter_chunks():
                    term_stdout.write(b'.')
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
    if not os.path.isdir(os.path.join(release_path, 'manage')) \
            or not os.path.isdir(os.path.join(release_path, 'system')):
        raise FileNotFoundError(
            f"possible broken release [system]: {version}: missing 'manage' or 'system'!"
        )
    todeploy: List[str] = [
        'manage',
        'system',
        'build.json',
        'init.sh',
        'server.py',
        'tsconfig.json',
        'webpack.config.js'
    ]
    for dfn in todeploy:
        print(f"deploying {dfn}")
        dest_fqfn: str = os.path.join(config.PRJROOT, dfn)
        repo_fqfn: str = os.path.join(release_path, dfn)
        if os.path.isdir(dest_fqfn):
            shutil.rmtree(dest_fqfn, ignore_errors=True)
        elif os.path.isfile(dest_fqfn):
            os.unlink(dest_fqfn)
        if os.path.isdir(repo_fqfn):
            shutil.copytree(repo_fqfn, dest_fqfn)
        else:
            shutil.copy(repo_fqfn, dest_fqfn)


def write_system_version(version: str) -> None:
    version_fn: str = os.path.join(config.PRJROOT, '.version')
    with open(version_fn, 'w') as f:
        f.write(version)


async def after_system_upgraded() -> None:
    await build.execute()


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

