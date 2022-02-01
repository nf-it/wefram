""" Build the necessary frontend requirements depending on the
project build configuration and installed apps. """

import os
from typing import *
from ..routines import frontend, start_project
from ... import ui, config
from ...tools import json_encode_custom, json_decode_from_file


build_defaults: dict = start_project.BUILD_JSON
build_conf: dict = config.BUILD_CONF
build_frontend: dict = build_conf.get('frontend') or build_defaults['frontend']


def _make_screens() -> None:
    schema: dict = ui.screens.as_json()
    items: str = json_encode_custom(schema, indent=2).lstrip('{').rstrip('}').strip('\n')
    frontend.with_template('screens.ts', items=items)


def _make_components() -> None:
    fn: str = os.path.join(config.BUILD_ROOT, 'frontend', 'components.ts')
    if os.path.isfile(fn):
        os.unlink(fn)
    components: dict = build_frontend.get('components') or build_defaults['frontend']['components']
    if not components:
        raise EnvironmentError(
            "The project's <build.json> has no 'frontend/components' section describing"
            " whose components to use for the frontend build!!!"
        )
    contents: List[str] = []
    for component_name, component_path in components.items():
        contents.append(
            f"import {component_name} from '{component_path}'"
        )

    contents.append("export {")
    contents.append(','.join(components.keys()))
    contents.append("}")

    with open(fn, 'w') as f:
        f.write('\n'.join(contents))


def _make_theme() -> None:
    fn: str = os.path.join(config.BUILD_ROOT, 'frontend', 'theme.ts')
    if os.path.isfile(fn):
        os.unlink(fn)
    theme: str = build_frontend.get('theme') or build_defaults['frontend']['theme'] or 'system/project/theme'
    with open(fn, 'w') as f:
        f.write(f"import workspaceTheme from '{theme}'\n")
        f.write("export {workspaceTheme}\n")


def run(*_) -> None:
    _make_screens()
    _make_components()
    _make_theme()

