"""
Provides the project settings routines, functionality to get and save
the one or the another settings entity.
"""

from typing import *
from ..tools import get_calling_app
from ..runtime import context
from ..models import SettingsCatalog
from . import entities, props
from .. import exceptions, ds


__all__ = [
    'get',
    'update',
    'reset',
    'drop'
]


def _entity_name_for(entity: Optional[str]) -> str:
    entity_name: str
    if entity and '.' in entity:
        app_name: str
        entity_sub: str
        app_name, entity_sub = entity.split('.', 1)
        return '.'.join([s for s in (app_name, entity_sub) if s])
    else:
        return '.'.join([s for s in (get_calling_app(), entity) if s])


async def get(
        entity: Optional[str] = None,
        force_user_id: [bool, str, None] = False
) -> SettingsCatalog:
    """ Fetches the specified entity and returns it to the caller.

    Speaking about personalized settings, the next logic will be used when fetching
    the settings entity:

    * If the argument ``force_user_id`` is set to ``None`` - the global scoped settings
        will be fetched;
    * If the argument ``force_user_id`` is set to the specific user's ``id`` - the
        personalized settings for the given user will be returned;
    * If the argument ``force_user_id`` is omitted and the current context user is not
        logged in - the global scoped entity will be returned;
    * If the argument ``force_user_id`` is omitted and the current context user IS
        logged in - then his|her scoped settings entity will be fetched, IF he or she
        has the saved one;
    * Otherwise, the global scoped settings entity will be fetched.

    :param entity:
        The name of the corresponding settings entity. If the name of the entity's parent
        application is omitted - the calling application will be considered the parent one;
        otherwise, if the entity is given in the format "<app_name>.<entity_name>", then
        the given application's entity will be fetched. This makes possible to get settings
        in one app from the another one.
    :type entity:
        str

    :param force_user_id:
        Optional argument provides ability to get the settings entity for the specified user
        instead of global scoped.
    """

    entity_name: str = _entity_name_for(entity)
    if entity_name not in entities.registered:
        raise RuntimeError(
            f"settings has no requested entity '{entity_name}'"
        )
    entity: entities.SettingsEntity = entities.registered[entity_name]

    user_id: Optional[str]
    if entity.allow_personals:
        context_user: Optional[str] = context['user'].user_id if 'user' in context else None
        user_id = force_user_id if force_user_id is not False else context_user
    else:
        user_id = None

    if entity_name not in context['settings']:
        context['settings'][entity_name]: Dict[str, SettingsCatalog] = dict()

    if user_id not in context['settings'][entity_name]:
        context['settings'][entity_name][user_id] = await SettingsCatalog(entity, user_id).load()

    return context['settings'][entity_name][user_id]


async def getall(force_user_id: [bool, str, None] = False) -> Dict[str, SettingsCatalog]:
    return {
        entity_name: await get(entity_name, force_user_id)
        for entity_name in entities.registered.keys()
    }


async def update(
        values: Dict[str, Any],
        entity: Optional[str] = None,
        force_user_id: [bool, str, None] = False,
        verify_permitted: bool = False
) -> None:
    entity_name: str = _entity_name_for(entity)
    if entity_name not in entities.registered:
        raise RuntimeError(
            f"settings has no requested entity '{entity_name}'"
        )
    entity: entities.SettingsEntity = entities.registered[entity_name]
    if verify_permitted and not entity.is_permitted:
        raise exceptions.AccessDenied()

    catalog: SettingsCatalog = await get(entity_name, force_user_id)
    for key, value in values.items():
        prop: props.PropBase = entity.properties.get(key, None)
        if prop is None:
            continue
        current_value: Any = catalog.get(key, ...)
        if isinstance(prop, (props.ImageProp, props.FileProp)):
            current_file_id: Union[str, None] = current_value.file_id \
                if isinstance(current_value, ds.StoredFile) \
                else (... if current_value is ... else current_value)
            new_file_id: Union[str, None] = value.file_id \
                if isinstance(value, ds.StoredFile) \
                else (... if value is ... else value)
            if current_value is not ... and current_file_id is not None and current_file_id != new_file_id:
                ds.storages.remove_file(prop.entity, current_file_id)
        catalog[key] = value
    await catalog.save()


async def reset(
        values: Dict[str, Dict[str, Any]],
        force_user_id: [bool, str, None] = False,
        verify_permitted: bool = False
) -> None:
    [
        (await update(values[entity], entity, force_user_id, verify_permitted))
        for entity
        in values
    ]


async def drop(*entity_names: str) -> None:
    """ TODO drop specified entity(ies) restoring the default values. """
    pass

