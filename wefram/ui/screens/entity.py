"""
An automation screens whose given an ability to skip creating frontend code
for every simple entity model.

Very useful for administrative screens whose administers simple ORM models like
directories.
"""

from typing import *
from .base import CompositeScreen
from .types import EnumField


class EntityListScreen(CompositeScreen):
    """
    The automatically generating entity model's list screen.
    """

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """


class EntityTableScreen(CompositeScreen):
    """
    The automatically generating entity model's list screen.
    """

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """


class EntityCardScreen(CompositeScreen):
    """
    The automatically generating entity model's card screen.
    """

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """


class EntityAdminScreen(CompositeScreen):
    """
    The screen consists of both list (or table) and card.
    """

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """

    enum_variant: Literal['list', 'table'] = 'list'
    """ The variant how the listing screen will look like: as list or as table.
    Possible values are 'list' and 'table'. """

    table_columns: List = None
    """ Defines columns whose will be present on the table screen (if the table
    variant has been selected). The each table column must be defined as
    :py:mesh:~Column: class. """

    primary_column: Optional = None

