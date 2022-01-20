from typing import *
from ...types.l10n import L10nStr


FieldType = Literal[
    'string',           # Just a textual string (default)
    'number',           # The number
    'boolean',          # Yes or No (will be presented as Yes-No image)
    'icon',             # Icon (the value will be interpreted as src url)
    'date',             # Date in the strict form
    'date_time',        # Date & time in the strict form
    'date_nice',        # The nice, textual format of the date
    'date_time_nice',   # The nice, textual format of the date & time
]


class EnumField:
    """
    The column definition for the entity listing (enumerating) screen.

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

    :param field_name:
        The name of the field, which must be the same as in the resulting
        data sent from backend to the frontend (the same as entity field name).

    :param caption:
        The field caption (strongly recommends to fill up this property for
        the table variant of enumerations). Might be lazy localized string for
        the localization purposes.

    :param caption_hint:
        If set, the field caption will be followed with the hint icon and
        the user will get the hint when moving mouse over the field caption hint

    :param textual:
        If set to ``true`` - the several field type-based variants, like ``boolean``,
        will be shown to the user textual, avoiding using of icons, images or etc.

    :param null_text:
        Defines behaviour on when the field value is ``null`` or avoided in the response. If
        not set - nothing will be rendered to the user (nothing shown). If set to the boolean ``true`` -
        the textual dash (-) will be rendered. If set to some string value - this string value will be
        shown to the user instead of null.

    :param value_visualize:
        The dictionary describing values and accordning textual
        representations. This allows to determine whether the raw value corresponds to the displayed
        textual value to the user.

    """

    def __init__(
            self,
            field_name: str,
            field_type: FieldType = 'string',
            caption: Optional[Union[str, L10nStr]] = None,
            caption_hint: Optional[Union[str, L10nStr]] = None,
            textual: bool = False,
            null_text: Optional[Union[bool, str]] = None,
            value_visualize: Optional[dict] = None
    ):
        self.field_name = field_name
        self.field_type = field_type
        self.caption = caption
        self.caption_hint = caption_hint
        self.textual = textual
        self.null_text = null_text
        self.value_visualize = value_visualize

    def as_json(self) -> dict:
        return {
            'fieldName': self.field_name,
            'fieldType': self.field_type,
            'caption': self.caption,
            'captionHint': self.caption_hint,
            'textual': self.textual,
            'nullText': self.null_text,
            'valueVisualize': self.value_visualize
        }

