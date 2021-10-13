""" The database migration to fit the current models and relationships schema. """

from ..routines import project
from ...ds import migrate


async def run(*_) -> None:
    project.ensure_apps_loaded()
    await migrate.migrate()

