"""
Provides the platform-managed settings functionality. This module serves the
settings' entities registration and registry.
"""

from typing import *
from ..tools import CSTYLE, get_calling_app
from ..types.l10n import L10nStr
from ..types.settings import SettingsEntity, PropBase
from .. import logger


__all__ = [
    'registered',
    'register'
]


# Registry of declared settings entities, as dict. The entity names are
# dict keys, and dict values are corresponding entity objects.
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
    """ Registers the settings entity in the system. The entity is described as
    a set of this function arguments.

    :param properties:
        Declared the set of entity's properties. There are two possible variants on how those
        properties are declared:

        #. Using ``dict`` type. Keys of the dict represents the corresponding propertys'
            names. Sorting of properties among each other is possible by using the ``order``
            argument of each property. For example:

            ``
            settings.register(
                name='test',
                order=10,
                properties={
                    'test_prop': settings.StringProp("The test property", order=10),
                    'other_prop': settings.StringProp("Other prop", order=20)
                },
                default={
                    'test_prop': "The first value",
                    'other_prop': "The second value"
                }
            )
            ``
        #. Using ``list`` type, each item of which is ``tuple`` consists of the corresponding
            property name at the first position, and the property at the second one. Properties
            will be ordered by the corresponding placemnet in the list. For example:

            ``
            settings.register(
                name='test',
                order=10,
                properties=[
                    ('test_prop', settings.StringProp("The test property")),
                    ('other_prop', settings.StringProp("Other prop"))
                ],
                default={
                    'test_prop': "The first value",
                    'other_prop': "The second value"
                }
            )
            ``
    :type properties:
        dict | list

    :param defaults:
        Used to specify default values for declared in this entity properties. The ``dict``
        must be used, where keys means corresponding properties' names, the dict values
        represents properties' default values. For example:

        ``
        settings.register(
            ...
            defaults={
                'test_property': "The first default value",
                'another_prop': 100500
            }
        )
        ``
    :type defaults:
        dict

    :param name:
        The system name of this entity.
    :type name:
        Optional, str

    :param caption:
        The human readable name of the entity. This name will be rendered as the group
        name of properties of this entity on the settings screen. It is optional and if
        is omitted, the group of properties will be without caption.
    :type caption:
        Optional, str

    :param requires:
        The set of permission scopes required current user to have to be able to modify
        this entity of properties. If the user do not have required permissions - this entity
        will even not be rendered at the frontend.
    :type requires:
        Optional, List[str]

    :param allow_personals:
        If set to ``True`` - then the entity may be personalized for the logged in user.
        This provides the ability not only to declare and manage global (project-level)
        settings, but give a user the posibility to override several or all of them with
        own values. If set to ``False`` (default) - the entity will not support personalization
        and only global scope of settings will be in use.
    :type allow_personals:
        bool

    :param order:
        The order in which this entity will be rendered on the settings screen. The order
        is applicable for the application only, so entities will be sorted for the each
        application, not conflicting with entities from other applications.
        Note that this argument about to omitted if properties declares using ``list``
        variant.
    :type order:
        Optional, int

    :param tab:
        The system tab name where this entity is placed in.
    :type tab:
        Optional, str
    """

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
