from typing import *
import abc
from dataclasses import dataclass
from .l10n import L10nStr


__all__ = [
    'PropBase',
    'SettingsEntity'
]


class PropBase(abc.ABC):
    prop_type: str = None

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
    app_name: str
    name: str
    caption: str
    properties: Dict[str, PropBase]
    defaults: Dict[str, Any]
    requires: Optional[Union[str, List[str]]]
    allow_personals: bool = False
    order: Optional[int] = None
    tab: Optional[str] = None

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
        # If the current user has no rights on this entity - return None instead
        # of real schema.
        if not self.is_permitted:
            return None

        # The list of properties, each of whose extended with 'name'
        # extra key. If there is a value given within 'values'
        # kwargs - add 'value' key to the each property too.
        props: List[dict] = [
            {**prop.schemadef(), **{'name': name}, **({'value': values[name]} if name in values else {})}
            for name, prop in self.properties.items()
        ]

        # Generating the this entity's schema definition, ready to be
        # JSON-encoded.
        default_order: int = max([(p['order'] or 0) for p in props]) + 10
        return {
            'appName': self.app_name,
            'name': self.name,
            'caption': str(self.caption) if self.caption else None,
            'properties': sorted(props, key=lambda x: ((x['order'] if x['order'] is not None else default_order), x['caption']))
        }