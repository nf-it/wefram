""" Drops the project uploaded data, including all data in the relational database,
 Redis, and all uploaded files from the files directory, if any exists. After that,
 creates an initial schema and uploads the initial data.

 Other words, doing ``setup`` procedure.
"""

from typing import *
from .routines.tools import yesno
from .routines.project import ensure_apps_loaded
from . import make
from .. import setups


async def run(params) -> None:
    if not yesno(
        "This command will drop all tables in the current PostgreSQL and all"
        " keys in the Redis. It will erase all uploaded files and will destroy "
        " ALL DATA in the databases. Are you really sure???"
    ):
        print("Canceled")
        exit(1)

    ensure_apps_loaded()
    await setups.setup()

    if params and params[0] == 'demo':
        apps_for_demo: Optional[List[str]] = params[1:] or None
        await setups.demo(apps_for_demo)

    await make.run(['setup'])

