"""
An automation screens whose given an ability to skip creating frontend code
for every simple entity model.

Very useful for administrative screens whose administers simple ORM models like
directories.
"""

from typing import *
from ...types.l10n import L10nStr
from ...api.entities import get_entity, EntityAPI
from ...aaa import permitted
from .base import ManagedScreen
from .types import EnumField


class EntityScreen(ManagedScreen):
    """
    The screen consists of both list (or table) and card.
    """

    component = 'wefram/containers/EntityScreen'

    caption: Union[str, L10nStr] = None
    """ The caption for the screen. If omitted - will not be displayed. If set,
    this caption will be rendered at the top of the screen, prior to enumeration
    of items. May be localized using :func:`~wefram.l10n.lazy_gettext`. """

    entity: str = None
    """ The corresponding API-entity name for which this screen is for. """

    entity_caption: Union[str, L10nStr] = None
    """ The optional caption used in the notifications and messages when something about
    to be shown to the user with the entity name. Adviced to fill up this parameter, 
    because otherwise the system entity  name (the class name) will be used instead, 
    which is not really understandable to the end user."""

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

    avatar_color: Union[bool, str] = None
    """ The color of the avatar (if it is defined). Possible value types are:
    (a) `string` - the exact CSS color code, **or** the name of the field, 
    which's value to use as color code;
    (b) or `boolean` (set to `true` to automatically generate the avatar color
    basing on the item's alternative string). """

    avatar_field: str = None
    """ The name of the corresponding item's field name to use as avatar image 
    source. """

    batch_delete: bool = True
    """ Controls will the enumeration (list or table) has checkboxes rendered,
    allowing to select items for (the only possible action with several selected
    items) deletion. Note that if ``permit_delete`` doesn't permits deletion -
    checkboxes will not been rendered even if ``batch_delete`` is set to ``True``. """

    default_sort: str = None
    """ The name of the entity field used for default sourting options. If the
    default sorting about to be descending - prepend the name of the field with
    the `minus` character (like ``-myfield``). Note that this is optional
    property even if the sorting is about to be controlled - the defaullt
    sorting might be set using :py:prop:`wefram.ds.model.Meta.order` property
    of the corresponding ORM model class. """

    delete_confirm_message: Union[str, L10nStr] = None
    """ The text message which displays to the user (as model dialog) when he|she 
    clicks on "Delete". If omitted, the default, common warning will be shown instead. """

    empty_list_text: Union[str, L10nStr] = None
    """ Optional parameter which defines the text which will be rendered to the end user
    if there are no items fetched as the API request. Possible value types are ``bool`` 
    (if set to ``True`` - display the default system text indicating that there are no 
    items in the list) or ``str`` (used to set the own text). """

    permit_search: bool = True
    """ If set to ``True`` - the search text input will be rendered, allowing
    a user to search over the entity (the entity must have findable fields
    declared). """

    permit_add: Union[bool, str, List[str]] = None
    """ If set to ``True`` - the Add button will be rendered allowing to add
    new objects of the corresponding entity. Set to ``False`` to disable the
    ability of adding new objects at all. If set to ``str`` or a list of ``str``,
    then the given permission(s) name(s) will be used to decide has the current
    user ability to add new object (do render the Add button) or not. Else, if
    not specified, the corresponding entity's permissions rules will be used
    to decide - has the user rights to create new object or has not. """

    permit_delete: Union[bool, str, List[str]] = None
    """ If set to ``True`` - the Delete button will be rendered allowing to remove
    objects of the corresponding entity. Set to ``False`` to disable the
    ability of removing objects at all. If set to ``str`` or a list of ``str``,
    then the given permission(s) name(s) will be used to decide has the current
    user ability to remove objects (do render the Delete button) or not. Else, if
    not specified, the corresponding entity's permissions rules will be used
    to decide - has the user rights to remove objects or has not. """

    provided_filters: dict = None
    """ Used to specify filters used in the request to the entity API. In
    opposition to the fully frontend programmed screen, specifying filters
    for the ``EntityScreen`` screen is a primaryly static option, allowing to
    exclude some content from the enumeration. Filters about to being provided
    as dict, with keys whose are filters' names and corresponding values. For
    example:
    
    .. highlight:: python
    .. code-block:: python
    
        class MyEntityScreen(EntityScreen):
            ...
            provided_filters = {
                'enabled': True,
                'role': 'regular',
                'other_option': 'some other value'
            }
    """

    filters_empty_allowed: bool = False
    """ By default, if the any filter's value is the empty string - this filter
    ignores and will not be included in the API request. This parameter is for 
    avoiding of this behaviour and passing empty string as the corresponding filter 
    value (even if the value is empty, yes). This parameter is a list of filters 
    names for which this behaviour is applicable to. """

    async def on_render(self) -> Any:

        def _is_permitted(local_prop: str, entity_prop: str) -> bool:
            _local: Any = getattr(self, local_prop)
            if isinstance(_local, bool):
                return _local

            # Here we'll check permissions of the EntityAPI model. Note that we will
            # ignore 'EntityAPI.requires' property, especially. This is because if the
            # current user, basing on that property, has no access to the screen at all,
            # then there is no option on rendering the button because the entire screen
            # will NOT be able to be opened at all.
            _scopes_req = _local \
                if isinstance(_local, (str, list, tuple)) \
                else getattr(entity, entity_prop)

            # If there are no permissions required - consider the positive ability
            if not _scopes_req:
                return True

            # Otherwise, check the given access rights
            else:
                return permitted(_scopes_req)

        entity_name: str = self.entity
        if not entity_name or not isinstance(entity_name, str):
            raise RuntimeError(
                "ManagedScreen.entity must be set and be the name of the corresponding entity!"
            )

        # We need both app name and entity name to generate the request path on the
        # frontend side. The developer might specify the entity without app name
        # (not using form ``<app_name>.<EntityName>``), and then the screen's app
        # name will be used as the entity's app name. Otherwise, if the app name
        # was specified in the name of the entity - the specified one will be used.
        entity_app: str
        if '.' in entity_name:
            entity_app, entity_name = entity_name.split('.', 1)
        else:
            entity_app = self.app
            entity_name = entity_name

        # Try to find out the registered entity
        entity_fqname: str = '.'.join([entity_app, entity_name])
        entity: ClassVar[EntityAPI] = get_entity(entity_fqname)
        if entity is None:
            raise RuntimeError(
                f"ManagedScreen.entity={entity_fqname} does not exists!"
            )

        # Handling buttons
        add_button: bool = _is_permitted('permit_add', 'allow_create')
        delete_button: bool = _is_permitted('permit_delete', 'allow_delete')

        # Preparing and returning the managerProps data. First, halding non-
        # optional (against the type) values.
        props: dict = {
            'entityApp': entity_app,
            'entityName': entity_name,
            'emumVariant': self.enum_variant or 'list',
            'addButton': add_button,
            'batchDelete': delete_button and self.batch_delete,
            'deleteButton': delete_button,
            'search': bool(self.permit_search),
            'filtersEmptyAllowed': bool(self.filters_empty_allowed)
        }

        # Handling the common properties
        if self.avatar_color:
            props['avatarClor'] = self.avatar_color
        if self.avatar_field:
            props['avatarField'] = self.avatar_field
        if self.caption:
            props['caption'] = str(self.caption)
        if self.entity_caption:
            props['entityCaption'] = str(self.entity_caption)
        if self.default_sort:
            props['defaultSort'] = {
                'value': self.default_sort[1:],
                'direction': 'desc'
            } if self.default_sort.startswith('-') else {
                'value': self.default_sort,
                'direction': 'asc'
            }
        if self.delete_confirm_message:
            props['deleteConfirmMessage'] = str(self.delete_confirm_message)
        if self.empty_list_text:
            props['emptyListText'] = str(self.empty_list_text)
        if self.provided_filters:
            props['providedFilters'] = self.provided_filters

        # Handling the 'list' variant
        if self.enum_variant == 'list':
            pass

        # Handling the 'table' variant
        elif self.enum_variant == 'table':
            pass

        return props

