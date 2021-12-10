from typing import *
import uuid
import os.path
import shutil
import csscompressor
import jsmin
from ... import config, logger
from ...tools import CSTYLE, module_path


__all__ = [
    'run'
]


STATICS_ASSETS_ROOT: str = os.path.join(config.STATICS_ROOT, 'assets')
STATICS_FONTS_ROOT: str = os.path.join(config.STATICS_ROOT, 'fonts')


def run(roots: List[str]) -> None:
    assets_uuid: str = uuid.uuid4().hex

    build_assets_root()
    make_dist(roots)
    make_fonts(roots)
    make_styles(roots, assets_uuid)
    make_scripts(roots, assets_uuid)
    # make_dists(roots)

    with open(os.path.join(config.STATICS_ROOT, 'assets.uuid'), 'w') as f:
        f.write(assets_uuid)


def build_assets_root() -> None:
    """ Removes old files from the assets directory and create the new one. """
    shutil.rmtree(STATICS_ASSETS_ROOT, ignore_errors=True)
    os.makedirs(STATICS_ASSETS_ROOT, exist_ok=True)


def path_from_root(root: str) -> Optional[str]:
    try:
        return module_path(root)
    except ModuleNotFoundError:
        return None


def make_scripts(roots: List[str], assets_uuid: str) -> None:
    contents: List[str] = []
    embed: List[str] = []
    logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}]")

    # The first step about to merge first-loading
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        srcpath: str = os.path.join(rootpath, 'assets', 'js')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.js')])
        for source in sources:
            logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}/js/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                contents.append(f.read())
        embedpath: str = os.path.join(srcpath, 'embed')
        if os.path.isdir(embedpath):
            sources: List[str] = sorted([f for f in os.listdir(embedpath) if f.endswith('.js')])
            for source in sources:
                logger.info(f"embedding assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}/js/embed/{source}")
                with open(os.path.join(embedpath, source), 'r') as f:
                    embed.append(f.read())

    # And the second step, merging finallies
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        srcpath: str = os.path.join(rootpath, 'assets', 'js', 'finally')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.js')])
        for source in sources:
            logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}/js/finally/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                contents.append(f.read())

    # Now making the final asset
    if not contents and not embed:
        return

    contents: str = jsmin.jsmin('\n\n'.join(contents))
    embed: str = '\n\n'.join(embed)
    fn: str = f"{assets_uuid}.js"
    logger.info(f"building assets statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] -> writting {CSTYLE['red']}{fn}{CSTYLE['clear']}")
    with open(os.path.join(STATICS_ASSETS_ROOT, fn), 'w') as f:
        f.write('"use strict";\n\n')
        if embed:
            f.write(embed)
            f.write('\n\n')
        if contents:
            f.write(contents)


def make_styles(roots: List[str], assets_uuid: str) -> None:
    contents: List[str] = []
    embed: List[str] = []
    logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}]")

    # The first step about to merge first-loading
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        srcpath: str = os.path.join(rootpath, 'assets', 'css')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.css')])
        for source in sources:
            logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}/css/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                content: str = f.read() \
                    .strip() \
                    .replace('{{ PUBLIC_ASSETS }}', f'{config.STATICS_URL}/assets') \
                    .replace('{{ PUBLIC_FONTS }}', f'{config.STATICS_URL}/fonts') \
                    .replace('{{ APP_ASSETS }}', f'{config.STATICS_URL}/assets/{root}')
                contents.append(content)
        embedpath: str = os.path.join(srcpath, 'embed')
        if os.path.isdir(embedpath):
            sources: List[str] = sorted([f for f in os.listdir(embedpath) if f.endswith('.css')])
            for source in sources:
                logger.info(f"embedding assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}/css/embed/{source}")
                with open(os.path.join(embedpath, source), 'r') as f:
                    embed.append(f.read())

    # And the second step, merging finallies
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        srcpath: str = os.path.join(rootpath, 'assets', 'css', 'finally')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.css')])
        for source in sources:
            logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}/css/finally/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                content: str = f.read() \
                    .strip() \
                    .replace('{{ PUBLIC_ASSETS }}', f'{config.STATICS_URL}/assets') \
                    .replace('{{ PUBLIC_FONTS }}', f'{config.STATICS_URL}/fonts') \
                    .replace('{{ APP_ASSETS }}', f'{config.STATICS_URL}/assets/{root}')
                contents.append(content)

    # Now making the final asset
    if not contents and not embed:
        return

    contents: str = csscompressor.compress('\n\n'.join(contents))
    embed: str = '\n\n'.join(embed)
    fn: str = f"{assets_uuid}.css"
    logger.info(f"building assets statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] -> writting {CSTYLE['red']}{fn}{CSTYLE['clear']}")
    with open(os.path.join(STATICS_ASSETS_ROOT, fn), 'w') as f:
        if embed:
            f.write(embed)
            f.write('\n\n')
        if contents:
            f.write(contents)


def make_dist(roots: List[str]) -> None:
    logger.info(f"building assets statics [{CSTYLE['bold']}DIST{CSTYLE['clear']}]")
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        fqpath: str = os.path.join(rootpath, 'assets', 'dist')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}DIST{CSTYLE['clear']}] => {root}")
        apath: str = os.path.join(STATICS_ASSETS_ROOT, root)
        shutil.copytree(fqpath, apath)


def make_fonts(roots: List[str]) -> None:
    shutil.rmtree(STATICS_FONTS_ROOT, ignore_errors=True)
    os.makedirs(STATICS_FONTS_ROOT)
    logger.info(f"building assets statics [{CSTYLE['bold']}FONTS{CSTYLE['clear']}]")
    for root in roots:
        rootpath = path_from_root(root)
        if not rootpath:
            continue
        fqpath: str = os.path.join(rootpath, 'assets', 'fonts')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building assets statics [{CSTYLE['bold']}FONTS{CSTYLE['clear']}] => {root}")
        shutil.copytree(fqpath, STATICS_FONTS_ROOT, dirs_exist_ok=True)


