from typing import *
from .....types.l10n import L10nStr
from .....tools import json_encode
from ...types import Prop


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


class EnumField(Prop):
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


class EnumsSortingOption:
    def __init__(self, value: str, caption: Union[str, L10nStr]):
        self.value = value
        self.caption = caption

    def json(self) -> str:
        return json_encode({
            'value': self.value,
            'caption': str(self.caption)
        })

    def __str__(self):
        return self.json()

    def __repr__(self):
        return self.json()


EnumsSortingOptions = List[EnumsSortingOption]


class ProvEnumCommonProps(Prop):
    """
    The common set of props for enumerating lists and tables.

    :param request_path:
        The URL path which to use in the API request.
    :type request_path:
        str, required

    :param on_error_show_msg:
        The message which system show to the user if error occur.
    :type on_error_show_msg:
        str, default = None

    :param avatar_color:
        The color of the avatar (if it is defined). Possible value types are:
            * ``str`` - the exact CSS color code, **or** the name of the field, which's
                value to use as color code;
            * or ``bool`` (set to ``True`` to automatically generate the avatar color
                basing on the item's alternative string).
    :type avatar_color:
        str | bool, default = False

    :param avatar_field:
        The name of the corresponding item's field name to use as avatar image source.
    :type avatar_field:
        str, default = None

    :param entity_caption:
        The optional caption used in the notifications and messages when something about
        to be shown to the user with the entity name. Adviced to fill up this parameter,
        because otherwise the system entity name (the class name) will be used instead,
        which is not really understandable to the end user.
    :type entity_caption:
        str, default = None

    :param default_sort:
        Optional - the name of the entity field which use as default sorting option.
        Prepend this name with minus symbol ('-') to select descending sorting (for
        example: ``default_sort = '-last_name'``).
    :type default_sort:
        str, default = None

    :param empty_list_text:
        Optional parameter which defines the text which will be rendered to the end user
        if there are no items fetched as the API request. Possible value types are
        ``bool`` (if set to ``True`` - display the default system text indicating that
        there are no items in the list) or ``str`` (used to set the own text).
    :type empty_list_text:
        str, default = None

    :param provided_filters:
        The optional dictionary consists of filters' names as keys and corresponding values;
        these filters will be passed to the backend using standard API filtering mechanisms.
        Special case is using ``like`` & ``ilike`` filter names - those names used to perform
        search operation (see reference on :py:meth:`ds.model.Model.like` and
        py:meth:`ds.model.Model.ilike` accordingly).

        Note that while there is possible to provide dynamic filtering when using the
        enumerating component in the frontend code design, it is not possible to do that
        on the static composite screen generation, so the only purpose in this special
        case is to set the static filtering of results.
    :type provided_filters:
        dict, default = None

    :param filters_empty_allowed:
        By default, if the any filter's value is the empty string - this filter
        ignores and will not be included in the API request. This parameter is for avoiding of this behaviour
        and passing empty string as the corresponding filter value (even if the value is empty, yes). This
        parameter is a list of filters names for which this behaviour is applicable to.
    :type filters_empty_allowed:
        list, default = None

    :param item_key_field:
        The name of the key field of the item. By default, the name 'key' used as
        the item key, and if there is no 'key' field - the 'id' name will be used. If the item has other
        than one of those two names as a primary key - the name of this field must be set using this
        parameter.
    :type item_key_field:
        str, default = None

    :param item_route:
        If the item about to link to the any route and clicking on the item about to
        switch to the specific URL - this parameter must be set to the corresponding route URL. In
        addition, if the "{key}" is in the given URL - it will be replaced with the corresponding item
        primary key value (see `itemKeyField` above). So, the good route looks like:
        ``/myveryapp/myveryitem/{key}``
    :type item_route:
        str, default = None

    :param pagination:
        If set to `true` - the pagination will be used to display enumeration;
        the corresponding set of UI elements will be automatically rendered. Pagination uses API
        request arguments `offset` and `limit` to control the offset (the start position from which
        to select objects) and the quantity of fetching items.
    :type pagination:
        bool, default = False

    :param sort_options:
        The array of sort options. If set, the selection of sorting will be
        rendered to the end user, allowing to change the default sorting of items to another option.
    :type sort_options:
        EnumsSortingOptions (List[EnumsSortingOption]), default = None

    :param storage_entity:
        The name of the defined storage entity, used for the avatar rendering. Used in combination
        with `avatarField` parameter. For example: ``myapp.myentity``.
    :type storage_entity:
        str, default = None

    """

    def __init__(self, request_path: str, **props):
        self.props: dict = {
            'request_path': request_path,
            'on_error_show_msg': props.pop('on_error_show_msg', ...),
            'avatar_color': props.pop('avatar_color', ...),
            'avatar_field': props.pop('avatar_field', ...),
            'default_sort': props.pop('default_sort', ...),
            'empty_list_text': props.pop('empty_list_text', ...),
            'provided_filters': props.pop('provided_filters', ...),
            'filters_empty_allowed': props.pop('filters_empty_allowed', ...),
            'item_key_field': props.pop('item_key_field', ...),
            'item_route': props.pop('item_route', ...),
            'pagination': props.pop('pagination', ...),
            'sort_options': props.pop('sort_options', ...),
            'storage_entity': props.pop('storage_entity', ...)
        }



