""" Drops the project uploaded data, including all data in the relational database,
 Redis, and all uploaded files from the files directory. """

from .routines.tools import yesno
from .. import setups


async def run(*_) -> None:
    if not yesno(
        "This command will drop all tables in the current PostgreSQL and all"
        " keys in the Redis. It will erase all uploaded files and will destroy "
        " ALL DATA in the databases. Are you really sure???"
    ):
        print("Canceled")
        exit(1)
    await setups.drop()

