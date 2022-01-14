from typing import *
from .base import CompositeScreen


class EntityListScreen(CompositeScreen):
    entity: str = None


class EntityCardScreen(CompositeScreen):
    entity: str = None


class EntityAdminScreen(CompositeScreen):
    entity: str = None
    list_variant: Literal['list', 'table'] = 'list'
    list_columns: List = None

