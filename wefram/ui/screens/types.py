"""
Provides type definitions and basic classes used by screens.
"""

from typing import *
from dataclasses import dataclass
from ...types.l10n import L10nStr
from ...tools import py_to_json


__all__ = [
    'RouteParams',
    'Prop',
    'EnumsSortingOption',
    'EnumField'
]


RouteParams = List[str]


class Prop:
    """
    The base class used by managed screens' fields to form props.
    """

    props: dict = {}

    def as_json(self) -> dict:
        return {k: v for k, v in py_to_json(self.props) if v is not ...}


@dataclass
class EnumsSortingOption:
    """
    The sorting option definition used in the enumerating components.
    """

    value: str
    """ The actual field name (value) which to use in the API request. """

    caption: Union[str, L10nStr]
    """ The human-readable caption which to render in the interface. This one
    may be set using lazy localization with :py:func:`~wefram.l10n.lazy_gettext`. """

    def as_json(self) -> dict:
        return {
            'value': self.value,
            'caption': str(self.caption)
        }


class EnumField(Prop):
    """
    The column definition for the entity listing (enumerating).

    :param field_type:
        The type of the field or table column. This affects on how the
        corresponding value will be interpreted and shown to the user.

        Possible types are:

        * ``string`` - Just a textual string (default)
        * ``number`` - The number
        * ``boolean`` - Yes or No (will be presented as Yes-No image)
        * ``icon`` - Icon (the value will be interpreted as src url)
        * ``date`` - Date in the strict form
        * ``date_time`` - Date & time in the strict form
        * ``date_nice`` - The nice, textual format of the date
        * ``date_time_nice`` - The nice, textual format of the date & time
    :type field_type:
        str, default = 'string'

    :param field_name:
        The name of the field, which must be the same as in the resulting
        data sent from backend to the frontend (the same as entity field name).
    :type field_name:
        str, required

    :param caption:
        The field caption (strongly recommends to fill up this property for
        the table variant of enumerations). Might be lazy localized string for
        the localization purposes.
    :type caption:
        str, default = None

    :param caption_hint:
        If set, the field caption will be followed with the hint icon and
        the user will get the hint when moving mouse over the field caption hint
    :type caption_hint:
        str, default = None

    :param textual:
        If set to ``true`` - the several field type-based variants, like ``boolean``,
        will be shown to the user textual, avoiding using of icons, images or etc.
    :type textual:
        bool, default = False

    :param null_text:
        Defines behaviour on when the field value is ``null`` or avoided in the response. If
        not set - nothing will be rendered to the user (nothing shown). If set to the boolean ``true`` -
        the textual dash (-) will be rendered. If set to some string value - this string value will be
        shown to the user instead of null.
    :type null_text:
        bool | str, default = None

    :param value_visualize:
        The dictionary describing values and accordning textual
        representations. This allows to determine whether the raw value corresponds to the displayed
        textual value to the user.
    :type value_visualize:
        dict, default = None

    """

    def __init__(self, field_name: str, **props):
        self.props = {
            'field_name': field_name,
            'field_type': props.pop('field_type', 'string'),
            'caption': props.pop('caption', ...),
            'caption_hint': props.pop('caption_hint', ...),
            'textual': bool(props.pop('textual', False)),
            'null_text': props.pop('null_text', ...),
            'value_visualize': props.pop('value_visualize', ...)
        }
