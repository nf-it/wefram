"""
Provides project's statics collection mechanism used to copy statics
files from the corresponding build directory to the specified in the
``build.json`` path.

This might be useful for containered runtimes, for example - for the
Docker and/or Cubernates environments, where static files are served
with the some ingress nginx and about to be placed in the volumes.
"""

import os
from distutils.dir_util import copy_tree
from .. import config


async def run(_) -> None:
    os.makedirs(STATICS_DST, exist_ok=True)
    copy_tree(config.STATICS_ROOT, STATICS_DST)

