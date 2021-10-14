from typing import *
from ..tools import CSTYLE, get_calling_app
from ..types.l10n import L10nStr
from ..types.settings import SettingsEntity, PropBase
from .. import logger


__all__ = [
    'registered',
    'register'
]


registered: Dict[str, SettingsEntity] = dict()


def register(
        properties: Union[Dict[str, PropBase], List[Tuple[str, PropBase]]],
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
    if isinstance(properties, (list, tuple)):
        _properties = {}
        for ix, p in enumerate(properties):
            if len(p) != 2:
                raise ValueError(
                    "wefram.settings.register() -> properties must be type of dict or list,"
                    " consisting of tuples (<prop_name>, <prop>)!"
                )
            prop_name: str
            prop: PropBase
            prop_name, prop = p
            if not isinstance(prop_name, str) or not isinstance(prop, PropBase):
                raise ValueError(
                    "wefram.settings.register() -> properties must be type of dict or list,"
                    " consisting of tuples (<prop_name>, <prop>)!"
                )
            prop.order = prop.order if prop.order is not None else (ix + 1001)
            _properties[prop_name] = prop
        properties = _properties
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
