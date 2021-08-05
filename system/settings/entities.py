from typing import *
from dataclasses import dataclass
from ..tools import CSTYLE, get_calling_app
from ..l10n import L10nStr
from .. import logger
from .props import PropBase


__all__ = [
    'SettingsEntity',
    'registered',
    'register'
]


class ISettingsEntitySchema(TypedDict):
    appName: str
    name: str
    caption: Optional[str]
    properties: list


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
        scopes: aaa.IPermissions = \
            (list(self.requires) if isinstance(self.requires, (list, tuple)) else [self.requires, ]) \
            if self.requires \
            else None
        requires: Optional[List[str]] = None if not scopes else [
            ('.'.join([self.app_name, scope] if '.' not in scope else scope)) for scope in scopes
        ]
        return aaa.permitted(requires) if requires else True

    def schemadef(self, **values: Any) -> Optional[ISettingsEntitySchema]:
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


registered: Dict[str, SettingsEntity] = dict()


def register(
        properties: Dict[str, PropBase],
        defaults: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        caption: Optional[Union[str, L10nStr]] = None,
        requires: Optional[Union[str, List[str]]] = None,
        allow_personals: bool = False,
        order: Optional[int] = None,
        tab: Optional[str] = None
) -> None:
    app_name: str = get_calling_app()
    entity_name: str = '.'.join([s for s in (app_name, name) if s])
    logger.debug(
        f"declared settings entity {CSTYLE['green']}{entity_name}{CSTYLE['clear']}"
    )
    registered[entity_name] = SettingsEntity(
        app_name=app_name,
        name=entity_name,
        caption=caption,
        properties=properties,
        defaults=defaults or {},
        requires=requires,
        allow_personals=allow_personals,
        order=order,
        tab=tab
    )
