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
    """ Fetches the specified entity's data and returns it to the caller as the
    specied :py:class:`~wefram.models.settings.SettingsCatalog` object.

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

    Note that *settings* mechanics uses caching of its entities in the in-memory database
    (Redis) to decrease the amount of PostgreSQL selects.

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
        instead of the default logic. The ``None`` value may be used to override user's
        personalized entity even if the current context user is logged in and has the
        saved personalized entity.
    :type force_user_id:
        Optional, str|None

    :return:
        The :py:class:`~wefram.models.settings.SettingsCatalog` object.

    :raises:
        `RuntimeError` "settings has no requested entity" if the requested entity is not
        declared in the project. Usually this means misspelling the entity name in the
        program code of the one or the another applcation.
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
    """ The shortcut functions returning all declared entities' data for the given criteria. The
    only criteria is using ``force_user_id`` argument which is full described in the
    :py:func:`~wefram.settings.get` function.

    :return:
        A dict containing entities' names as keys and corresponding fetched catalogs as
        dict's values.
    """

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
    """
    Used to update the given entity's properties' values. May be used to update the
    settings entity's values catalog without fetching it first.

    :param values:
        The dict containing properties' names as keys, and corresponding new values.

    :param entity:
        The name of the corresponding settings entity. If the name of the entity's parent
        application is omitted - the calling application will be considered the parent one;
        otherwise, if the entity is given in the format "<app_name>.<entity_name>", then
        the given application's entity will be fetched. This makes possible to get settings
        in one app from the another one.

    :param force_user_id:
        Optional argument provides ability to set the settings of the entity for the specified
        user instead of the default logic. The ``None`` value may be used to override user's
        personalized entity even if the current context user is logged in and has the
        saved personalized entity.

    :param verify_permitted:
        By default, the responsibility for permission checking on the settings changes inside
        the program code is on the corresponding application's programmer. The point is that
        application programmer really understands when to update settings, and whose criteria
        must succeed to do that.
        In opposite, the application programmer might want to Wefram to check - has the current
        context user access right to update given entity's settings or do not. To enable this
        scenario this argument, being set to ``True``, might be used.
    """

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
    """ The same as :py:func:`~wefram.settings.update`, but allows to update several entitys' catalogs
    at once, using the higher-level dict, each key of which represents the corresponding entity name &
    the value represents the applicable to the :py:func:`~wefram.settings.update` values dict.
    """

    [
        (await update(values[entity], entity, force_user_id, verify_permitted))
        for entity
        in values
    ]


async def drop(*entity_names: str) -> None:
    """ TODO drop specified entity(ies) restoring the default values. """
    pass

