"""
Merges the full default configration (distributes with the Wefram platform)
with the current project configuration, stored as corresponding JSON
files:

* build.json
* config.json
* config.default.json

And writes the resulting, merged configurations in the corresponding JSON
files: 'build.json' and 'config.json'. This provides the full view of
available configuration options and structure, which makes easier to
maintain those settings.
"""


import os.path
from ... import config
from ..routines.tools import json_to_file, merge_conf
from ... import confskel


__all__ = [
    'run'
]


def run(*_) -> None:
    # Making the ``/build.json``
    print("Making `build.json`")
    json_to_file(
        merge_conf(confskel.BUILD_JSON, config.BUILD_CONF),
        os.path.join(config.PRJ_ROOT, "build.json")
    )

    # Making the ``/config.default.json``
    print("Making `config.default.json`")
    json_to_file(
        merge_conf(confskel.CONFIG_JSON, config.PROJECT_CONFIG_DEFAULT or {}),
        os.path.join(config.PRJ_ROOT, "config.default.json")
    )

    # Making the ``/config.json``. Write this config if is exist in the project only.
    if config.PROJECT_CONFIG:
        print("Making `config.json`")
        json_to_file(
            merge_conf(confskel.CONFIG_JSON, config.PROJECT_CONFIG),
            os.path.join(config.PRJ_ROOT, "config.json")
        )
    else:
        print("Skipping `config.json`")

    print("done")

