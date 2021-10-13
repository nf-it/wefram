from typing import *
from dataclasses import dataclass
from ...tools import CSTYLE, get_calling_app
from ... import logger


__all__ = [
    'StorageEntity',
    'registered',
    'register'
]


@dataclass
class StorageEntity:
    app: str
    name: str
    requires: Optional[List[str]]
    readable: Optional[List[str]]


registered: Dict[str, StorageEntity] = {}


def register(
        name: str,
        requires: Optional[List[str]] = None,
        readable: Optional[List[str]] = None,
        app: Optional[str] = None
) -> None:
    app_name: str
    if app is not None:
        app_name = app
    elif '.' in name:
        app_name, name = name.split('.', 2)
    else:
        app_name = get_calling_app()
    entity = StorageEntity(
        app=app_name,
        name=name,
        requires=requires,
        readable=readable
    )
    entity_name: str = '.'.join([app_name, name])
    registered[entity_name] = entity
    logger.debug(f"registered file storage entity {CSTYLE['red']}{entity_name}{CSTYLE['clear']}")

