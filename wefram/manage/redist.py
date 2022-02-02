"""
Recreates (and possible upgrades) the project's root from the skeleton. This
replaces the project's rooted files, like 'makefile', 'main.tsx', 'server.py',
'manage', etc., with the distributes ones.

If some of those files been modified by the project developer - all changes
will be lost.
"""

from typing import *
import os
import os.path
import shutil
from .. import config


async def run(_) -> None:
    for f in [
        z for z in os.listdir(os.path.join(config.CORE_ROOT, 'manage', 'dist', 'project'))
        if not z.startswith('.') and not z.startswith('_')
    ]:
        print(f"distributing: {f}")
        shutil.copyfile(
            os.path.join(config.CORE_ROOT, 'manage', 'dist', 'project', f),
            os.path.join(config.PRJ_ROOT, f)
        )
    print("done")
