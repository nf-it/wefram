import uuid
from typing import *
import types
import os
import os.path
import subprocess
import shutil
import csscompressor
import jsmin
import config
from system.tools import CSTYLE, json_encode_custom, app_dir, app_root
from system import logger, ui, apps, l10n


TS_TEMPLATES_ROOT: str = os.path.join(config.COREROOT, 'web', 'templates')
TS_PREPARED_ROOT: str = os.path.join(config.COREROOT, 'web', 'prepared')
STATICS_URL: str = config.STATICS_URL
STATICS_ROOT: str = config.STATICS_ROOT
STATICS_CSS_ROOT: str = os.path.join(STATICS_ROOT, 'css')
STATICS_JS_ROOT: str = os.path.join(STATICS_ROOT, 'js')
STATICS_MEDIA_ROOT: str = os.path.join(STATICS_ROOT, 'media')
STATICS_FONTS_ROOT: str = os.path.join(STATICS_ROOT, 'fonts')
STATICS_DIST_ROOT: str = STATICS_ROOT

ENSURE_DIRSTRUCT: List[str] = [
    TS_PREPARED_ROOT,
    STATICS_ROOT
]


def clean() -> None:
    [
        shutil.rmtree(os.path.join(STATICS_ROOT, f), ignore_errors=True)
        for f in os.listdir(STATICS_ROOT)
        if os.path.isdir(f) and f not in ENSURE_DIRSTRUCT
    ]


async def template_ts(template_fn: str, prepared_fn: Optional[str] = None, **kwargs) -> None:
    prepared_fn: str = prepared_fn or template_fn
    with open(os.path.join(TS_TEMPLATES_ROOT, template_fn), 'r') as template_f:
        content: str = template_f.read()
    for k, v in kwargs.items():
        content = content.replace(f"/* (%%{k}%%) */", v)
    with open(os.path.join(TS_PREPARED_ROOT, prepared_fn), 'w') as prepared_f:
        prepared_f.write(content)


async def clean_ts_prepared() -> None:
    shutil.rmtree(TS_PREPARED_ROOT)
    os.makedirs(TS_PREPARED_ROOT, exist_ok=True)


async def make_screens_ts() -> None:
    schema: ui.screens.ScreensSchema = ui.screens.as_json()
    items: str = json_encode_custom(schema, indent=2).lstrip('{').rstrip('}').strip('\n')
    await template_ts('screens.ts', items=items)


async def make_frontend(debug: Optional[bool] = None) -> None:
    env_mode: str = 'development' if debug is True or not config.PRODUCTION else 'production'
    command: str = 'build' if env_mode == 'production' else 'build-devel'
    subprocess.run(['yarn', command])


def ensure_dirstruct() -> None:
    for d in ENSURE_DIRSTRUCT:
        os.makedirs(d, exist_ok=True)


def make_statics(roots: List[str]) -> None:
    logger.info(f"building apps custom statics")
    os.makedirs(STATICS_ROOT, exist_ok=True)
    assets_uuid: str = uuid.uuid4().hex
    make_statics_media(roots)
    make_statics_fonts(roots)
    make_statics_css(roots, assets_uuid)
    make_statics_js(roots, assets_uuid)
    make_statics_dists(roots)
    with open(os.path.join(STATICS_ROOT, 'assets.uuid'), 'w') as f:
        f.write(assets_uuid)


def make_statics_js(roots: List[str], assets_uuid: str) -> None:
    shutil.rmtree(STATICS_JS_ROOT, ignore_errors=True)
    os.makedirs(STATICS_JS_ROOT)
    contents: List[str] = []
    embed: List[str] = []
    logger.info(f"building public statics [{CSTYLE['bold']}JS{CSTYLE['clear']}]")
    for root in roots:
        srcpath: str = os.path.join(config.PRJROOT, root, 'public', 'js')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building public statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.js')])
        for source in sources:
            logger.info(f"building public statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}/js/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                contents.append(f.read())
        embedpath: str = os.path.join(srcpath, 'embed')
        if os.path.isdir(embedpath):
            sources: List[str] = sorted([f for f in os.listdir(embedpath) if f.endswith('.js')])
            for source in sources:
                logger.info(f"embedding public statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] => {root}/js/{source}")
                with open(os.path.join(embedpath, source), 'r') as f:
                    embed.append(f.read())
    if not contents and not embed:
        return
    contents: str = jsmin.jsmin('\n\n'.join(contents))
    embed: str = '\n\n'.join(embed)
    fn: str = f"assets.{assets_uuid}.js"
    logger.info(f"building public statics [{CSTYLE['bold']}JS{CSTYLE['clear']}] -> writting {CSTYLE['red']}{fn}{CSTYLE['clear']}")
    with open(os.path.join(STATICS_JS_ROOT, fn), 'w') as f:
        if embed:
            f.write(embed)
            f.write('\n\n')
        if contents:
            f.write(contents)


def make_statics_css(roots: List[str], assets_uuid: str) -> None:
    shutil.rmtree(STATICS_CSS_ROOT, ignore_errors=True)
    os.makedirs(STATICS_CSS_ROOT)
    contents: List[str] = []
    embed: List[str] = []
    logger.info(f"building public statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}]")
    for root in roots:
        srcpath: str = os.path.join(config.PRJROOT, root, 'public', 'css')
        if not os.path.isdir(srcpath):
            continue
        logger.info(f"building public statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}")
        sources: List[str] = sorted([f for f in os.listdir(srcpath) if f.endswith('.css')])
        for source in sources:
            logger.info(f"building public statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}/css/{source}")
            with open(os.path.join(srcpath, source), 'r') as f:
                content: str = f.read() \
                    .strip() \
                    .replace('{{ PUBLIC_MEDIA }}', f'{STATICS_URL}/media') \
                    .replace('{{ PUBLIC_FONTS }}', f'{STATICS_URL}/fonts') \
                    .replace('{{ APP_MEDIA }}', f'{STATICS_URL}/media/{root}')
                contents.append(content)
        embedpath: str = os.path.join(srcpath, 'embed')
        if os.path.isdir(embedpath):
            sources: List[str] = sorted([f for f in os.listdir(embedpath) if f.endswith('.css')])
            for source in sources:
                logger.info(f"embedding public statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] => {root}/css/{source}")
                with open(os.path.join(embedpath, source), 'r') as f:
                    embed.append(f.read())
    if not contents and not embed:
        return
    contents: str = csscompressor.compress('\n\n'.join(contents))
    embed: str = '\n\n'.join(embed)
    fn: str = f"assets.{assets_uuid}.css"
    logger.info(f"building public statics [{CSTYLE['bold']}CSS{CSTYLE['clear']}] -> writting {CSTYLE['red']}{fn}{CSTYLE['clear']}")
    with open(os.path.join(STATICS_CSS_ROOT, fn), 'w') as f:
        if embed:
            f.write(embed)
            f.write('\n\n')
        if contents:
            f.write(contents)


def make_statics_media(roots: List[str]) -> None:
    shutil.rmtree(STATICS_MEDIA_ROOT, ignore_errors=True)
    os.makedirs(STATICS_MEDIA_ROOT)
    logger.info(f"building public statics [{CSTYLE['bold']}MEDIA{CSTYLE['clear']}]")
    for root in roots:
        fqpath: str = os.path.join(config.PRJROOT, root, 'public', 'media')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building public statics [{CSTYLE['bold']}MEDIA{CSTYLE['clear']}] => {root}")
        root_statics_dir: str = root \
            if not root.startswith(f"{config.APPSDIR}/") \
            else os.path.join(*root.split(os.path.sep)[1:])
        apath: str = os.path.join(STATICS_MEDIA_ROOT, root_statics_dir)
        shutil.copytree(fqpath, apath)


def make_statics_fonts(roots: List[str]) -> None:
    shutil.rmtree(STATICS_FONTS_ROOT, ignore_errors=True)
    os.makedirs(STATICS_FONTS_ROOT)
    logger.info(f"building public statics [{CSTYLE['bold']}FONTS{CSTYLE['clear']}]")
    for root in roots:
        fqpath: str = os.path.join(config.PRJROOT, root, 'public', 'fonts')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building public statics [{CSTYLE['bold']}FONTS{CSTYLE['clear']}] => {root}")
        apath: str = STATICS_FONTS_ROOT
        shutil.copytree(fqpath, apath, dirs_exist_ok=True)


def make_statics_dists(roots: List[str]) -> None:
    logger.info(f"building public statics [{CSTYLE['bold']}DIST{CSTYLE['clear']}]")
    for root in roots:
        fqpath: str = os.path.join(config.PRJROOT, root, 'public', 'dist')
        if not os.path.isdir(fqpath):
            continue
        logger.info(f"building public statics [{CSTYLE['bold']}DIST{CSTYLE['clear']}] => {root}")
        apath: str = STATICS_ROOT
        shutil.copytree(fqpath, apath, dirs_exist_ok=True)


def make_statics_only(apps_to_build: Optional[List[str]] = None) -> None:
    logger.set_level(max(logger.VERBOSITY, logger.INFO))

    if not apps_to_build:
        apps_to_build: List[str] = apps.get_apps_loaded()

    roots: List[str] = []
    if config.ASSETS_DIR:
        roots.append(config.ASSETS_DIR)

    for name in apps_to_build:
        _root: str = app_root(name)
        if not os.path.isdir(_root):
            raise FileNotFoundError(
                f"app '{name}' has not been found (not installed, but enabled?)"
            )
        roots.append(app_dir(name))

    clean()
    ensure_dirstruct()
    make_statics(roots)
    l10n.build.make()


async def make(apps_to_build: Optional[List[str]] = None) -> None:
    logger.set_level(max(logger.VERBOSITY, logger.INFO))

    shutil.rmtree(config.STATICS_ROOT, ignore_errors=True)
    os.makedirs(config.STATICS_ROOT)
    ensure_dirstruct()

    if not apps_to_build:
        apps_to_build: List[str] = apps.get_apps_loaded()

    roots: List[str] = []
    if config.ASSETS_DIR:
        roots.append(config.ASSETS_DIR)

    ctx: dict = dict()
    ctx['apps']: List[str] = apps_to_build
    ctx['apps_build']: Dict[str, types.ModuleType] = dict()

    makes: List[Tuple[str, callable]] = []

    for name in apps_to_build:
        _root: str = app_root(name)
        if not os.path.isdir(_root):
            raise FileNotFoundError(
                f"app '{name}' has not been found (not installed, but enabled?)"
            )

        roots.append(app_dir(name))

        if name == config.COREDIR or name == 'system':
            continue

        _module: types.ModuleType = apps.modules[name]
        if not hasattr(_module, 'build'):
            continue
        _build: Any = getattr(_module, 'build')
        if not isinstance(_module, types.ModuleType):
            raise TypeError(
                f"'{name}'.build must be module, get the '{type(_build)}' instead"
            )
        _make: callable = getattr(_build, 'make', None)
        if _make is None:
            continue
        if not callable(_make):
            raise TypeError(
                f"{name}.build.make is not an async callable coroutine"
            )
        makes.append((name, _make))
        ctx['apps_build'][name] = _build

    for _make in makes:
        name: str
        func: callable
        name, func = _make
        logger.info(f"Build {CSTYLE['bold']}{name}{CSTYLE['clear']}")
        await func(ctx)

    await clean_ts_prepared()
    make_statics(roots)
    l10n.build.make()
    await make_screens_ts()
    await make_frontend()
