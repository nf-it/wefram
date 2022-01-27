"""
Provides types for settings and properties management system.
"""

from typing import *
import abc
from dataclasses import dataclass
from .l10n import L10nStr


__all__ = [
    'PropBase',
    'SettingsEntity'
]


class PropBase(abc.ABC):
    """
    Abstract class for the any settings property definition.
    """

    prop_type: str = None
    """ The declared type of the property. Used by the frontend code to render the
    corresponding component. """

    def __init__(
            self,
            caption: Union[str, L10nStr],
            order: Optional[int] = None
    ):
        self.caption = caption
        self.order = order

    def schemadef(self) -> dict:
        return {
            'fieldType': self.prop_type,
            'caption': str(self.caption),
            'order': self.order
        }


@dataclass
class SettingsEntity:
    """
    The settings entity. Any application may have any quanity of settings entities, divided
    by the understandable and appropriate logic. Each entity stores a set of properties, declared
    by corresponding, inherited from the :py:class:`PropBase` class. And each entity renders on
    the client side, on the settings page, as a separate group of properties with optional
    group caption (see ``caption`` property below).
    """

    app_name: str
    """ The corresponding application name for the entity. Each entity is owned by the one or the
    another application. This provides the corresponding settings placement on the settings screen
    and posibility to avoid any conflicts based on name re-using by different applications. """

    name: str
    """ The system name of the entity. """

    caption: str
    """ The human-readable name which will be rendered as the caption of the corresponding
    group of properties. Optional and may be omitted. """

    properties: Dict[str, PropBase]
    """ A set of properties formed as Python dict, where keys are properies' names and
    corresponding properties' classes as values. """

    defaults: Dict[str, Any]
    """ The dict contains of default values for declared properties. If the property is
    declared, but it does not exists in the database - the default value will be used.
    This may happen, for example, on the first application use or when the application
    developer adds a new property and, accordently, there is no stored property value
    yet. And the another approach of the default propery is the 'Reset to defaults'
    procedure, which can drop all properties values, reverting to the default ones. """

    requires: Optional[Union[str, List[str]]]
    """ The set of permission scopes required current user to have to be able to modify
    this entity of properties. If the user do not have required permissions - this entity
    will even not be rendered at the frontend. """

    allow_personals: bool = False
    """ If set to ``True`` - then the entity may be personalized for the logged in user.
    This provides the ability not only to declare and manage global (project-level)
    settings, but give a user the posibility to override several or all of them with
    own values. If set to ``False`` (default) - the entity will not support personalization
    and only global scope of settings will be in use. """

    order: Optional[int] = None
    """ The order in which this entity will be rendered on the settings screen. The order
    is applicable for the application only, so entities will be sorted for the each
    application, not conflicting with entities from other applications. """

    tab: Optional[str] = None
    """ Optional name of the settings tab. 
    TODO! describe more detailed. """

    @property
    def namesub(self) -> Optional[str]:
        if '.' not in self.name:
            return None
        parts: List[str] = self.name.split('.', 1)
        if len(parts) == 1:
            return None
        return parts[1]

    @property
    def is_permitted(self) -> bool:
        """ Returns ``True`` if the current user has access to this entity, and ``False`` otherwise. """

        from .. import aaa

        scopes: List[str] = \
            (list(self.requires) if isinstance(self.requires, (list, tuple)) else [self.requires, ]) \
            if self.requires \
            else None
        requires: Optional[List[str]] = None if not scopes else [
            ('.'.join([self.app_name, scope] if '.' not in scope else scope)) for scope in scopes
        ]

        return aaa.permitted(requires) if requires else True

    def schemadef(self, **values: Any) -> Optional[dict]:
        """ Returns the entity schema used by the frontend to render the settings. If the current
        user has no permissions to this entity - return ``None``.
        """

        # If the current user has no rights on this entity - return None instead
        # of real schema.
        if not self.is_permitted:
            return None

        # The list of properties, each of whose extended with 'name'
        # extra key. If there is a value given within 'values'
        # kwargs - add 'value' key to each property too.
        props: List[dict] = [
            {**prop.schemadef(), **{'name': name}, **({'value': values[name]} if name in values else {})}
            for name, prop in self.properties.items()
        ]

        # Generating this entity's schema definition, ready to be
        # JSON-encoded.
        default_order: int = max([(p['order'] or 0) for p in props]) + 10
        return {
            'appName': self.app_name,
            'name': self.name,
            'caption': str(self.caption) if self.caption else None,
            'properties': sorted(props, key=lambda x: ((x['order'] if x['order'] is not None else default_order), x['caption']))
        }
