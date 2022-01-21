"""
An automation screens whose given an ability to skip creating frontend code
for every simple entity model.

Very useful for administrative screens whose administers simple ORM models like
directories.
"""

from typing import *
from ...types.l10n import L10nStr
from .base import ManagedScreen
from .components.ProvEnums.types import EnumField


class EntityScreen(ManagedScreen):
    """
    The screen consists of both list (or table) and card.
    """

    component = 'containers/EntityScreen'

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """

    enum_variant: Literal['list', 'table'] = 'list'
    """ The variant how the listing screen will look like: as list or as table.
    Possible values are 'list' and 'table'. """

    table_columns: List[EnumField] = None
    """ Defines columns whose will be present on the table screen (if the table
    variant has been selected). The each table column must be defined as
    :py:meth:`~EnumField` class instance. """

    primary_field: Union[EnumField, List[EnumField]] = None
    """ Defines the primary field for the ``list`` variant of enum. If the
    several fields needs to be placed next to each other - group them using
    list or tuple. """

    secondary_field: Union[EnumField, List[EnumField]] = None
    """ Defines the secondary field for the ``list`` variant of enum. If the
    several fields needs to be placed next to each other - group them using
    list or tuple. """

    async def on_render(self) -> Any:
        return {
            'test': 'THE TESTING'
        }

