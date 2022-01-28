"""
Provides models, both ORM (persistent storage) and runtime, for the
settings facility of the Wefram platform.
"""

from typing import *
from collections import UserDict
from .. import ds, logger
from ..tools import CSTYLE, json_decode, json_encode
from ..types.settings import SettingsEntity, PropBase


__all__ = [
    'SettingsCatalog',
    'StoredSettings'
]


class SettingsCatalog(UserDict):
    """
    The runtime class providing loading and saving settings for the
    corresponding entity. When the application uses the
    :py:func:`wefram.settings.get` function to load settings for the
    given entity - this class based instance returns to the calling
    code.
    """

    def __init__(self, entity: SettingsEntity, user_id: Optional[str]):
        from ..settings import entities

        super().__init__()

        if entity.name not in entities.registered:
            raise RuntimeError(
                f"settings has no requested entity '{entity.name}'"
            )
        self.entity_name: str = entity.name
        self.entity: SettingsEntity = entity
        self.user_id: Optional[str] = user_id

    def __getitem__(self, key):
        """ Returns the settings value by the key, using dict-like access:
        ``prop_value = some_settings['some_prop']``
        """

        if key not in self.entity.properties:
            raise KeyError(f"settings entity '{self.entity_name}' has no property '{key}'")
        item: Any = super().__getitem__(key)
        prop: PropBase = self.entity.properties[key]

        if prop.prop_type == 'image':
            return ds.StoredImage(getattr(prop, 'entity'), item)
        elif prop.prop_type == 'file':
            return ds.StoredFile(getattr(prop, 'entity'), item)

        return item

    def __setitem__(self, key, value):
        """ Updates the settings value, using dict-like access:
        ``some_settings['some_prop'] = 'some_value'``
        """

        if key not in self.entity.properties:
            raise KeyError(f"settings entity '{self.entity_name}' has no property '{key}'")
        super().__setitem__(key, value)

    def __delitem__(self, key):
        """ Drops the settings value to the default one. The might
        be made using dict-like approach: ``del(some_settings['some_prop'])``
        """

        defaults: dict = self.entity.defaults or {}
        if key in defaults:
            super().__setitem__(key, defaults[key])
            return
        super().__delitem__(key)

    def __iter__(self):
        """ Iterate over settings' properties' values. """

        return super().__iter__()

    def redis_key(self, user_id: Optional[str]) -> str:
        """ Returns the Redis attribute key name to store values for this
        settings catalog. The format of the key name:

        ``settings:catalog:[user_id]:<entity_name>``

        """
        return ':'.join(['settings', 'catalog', (user_id or ''), self.entity_name])

    def load_defaults(self) -> None:
        """ Set properties' values to the default values (read from the entity
        declaration, from the ``defaults`` attribute).
        """

        self.data: Dict[str, Any] = self.entity.defaults or {}

    async def _save_to_redis(self, data: Optional[Dict[str, Any]], user_id: Optional[str]) -> None:
        """ Saves this catalog values to the Redis in-memory database. """

        redis_cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        key: str = self.redis_key(user_id)
        await redis_cn.set(key, json_encode(data))

    async def _load(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """ Loads this settings catalog's values for the given scope - the
        personalized one if the ``user_id`` is set to the corresponding user
        ``id``, of global one if it is equals to "GLOBAL". Read from the Redis in-memory
        cache if this entity (taking in account ``user_id``) exists in it. If the
        entity not exists in the Redis - try to load from the PostgreSQL database.
        If there is no saved catalog in the PostgreSQL database - the default
        values will be used instead.

        If the catalog is present in the PostgreSQL database and is not exists
        in the Redis - it will be saved to the Redis to fetch it faster next time.
        """

        # Try to fetch cached catalog from the Redis
        redis_cn: ds.redis.RedisConnection = await ds.redis.get_connection()
        key: str = self.redis_key(user_id)
        cached_catalog: Optional[str] = await redis_cn.get(key)

        if cached_catalog is None:
            # If there is no cached catalog in the Redis - try to load from
            # the PostgreSQL.
            stored_catalog: StoredSettings = await StoredSettings.first(
                entity=self.entity_name,
                user_id=user_id
            )
            catalog: StoredSettings = stored_catalog if stored_catalog is not None else None

            if catalog is not None:
                # If the catalog is present in the PostgreSQL - cache it to the Redis
                await self._save_to_redis(catalog.data, user_id)
                personality: str = "GLOBAL" if user_id is None else user_id
                logger.debug(
                    f"got {CSTYLE['red']}stored{CSTYLE['clear']} settings '{self.entity_name}' for '{personality}'",
                    '_load'
                )
                return catalog.data

            else:
                return None

        else:
            personality: str = "GLOBAL" if user_id is None else user_id
            logger.debug(
                f"got {CSTYLE['green']}cached{CSTYLE['clear']} settings '{self.entity_name}' for '{personality}'",
                '_load'
            )
            return json_decode(cached_catalog)

    def _ensure_defaults(self) -> None:
        for k, v in self.entity.defaults.items():
            if k in self.data:
                continue
            self.data[k] = v

    async def load(self) -> 'SettingsCatalog':
        """ Loads the settings catalog and returns to the calling function. Tries
        to fetch the personal catalog first, if is allowed by the entity policy,
        and if fail - the global scoped will be loaded.
        """

        # Trying to fetch personal catalog first, if is allowed by the entity policy
        if self.user_id is not None and self.entity.allow_personals:
            data: Optional[Dict[str, Any]] = await self._load(self.user_id)
            if data is not None:
                self.data = data
                self._ensure_defaults()
                return self

        # Trying to fetch global settings entity
        data: Optional[Dict[str, Any]] = await self._load(None)

        # If there is no any data present yet, even in the database storage:
        # (a) fill up the resulting SettingsCatalog with the default values
        # (b) store 'null' in the Redis cache to avoid repeatedly querying the
        #     database for the non existing values
        if data is None:
            self.data = {}
            self.load_defaults()
            if self.entity.allow_personals:
                await self._save_to_redis(None, self.user_id)
            await self._save_to_redis(None, None)
        else:
            self.data = data
            self._ensure_defaults()
            await self._save_to_redis(data, None)

        return self

    async def save(self, globally: Optional[bool] = None) -> None:
        """ Saves the settings catalog, storing all values both to the in-memory
        database (Redis) and to the PostgreSQL. If the ``globally`` set to
        ``True``, then settings will be saved in the global scope; if set to
        ``False`` or omitted - then settings will be saved personally if the
        catalog is personal, or globally otherwise.
        """

        user_id: Optional[str] = self.user_id if globally is None else (
            None if globally is True else self.user_id
        )

        stmt = ds.select(StoredSettings).where(ds.and_(
            StoredSettings.entity == self.entity_name,
            StoredSettings.user_id == user_id
        )).with_for_update()
        stored_catalog: StoredSettings = (await ds.db.execute(stmt)).scalars().first()
        if stored_catalog is None:
            stored_catalog = await StoredSettings.create(
                entity=self.entity_name,
                user_id=self.user_id
            )
        stored_catalog.data = self.data

        await self._save_to_redis(self.data, user_id)


class StoredSettings(ds.Model):
    """
    The settings catalog model. Used to save settings permanently
    to the PostgreSQL database.
    """

    id = ds.UUIDPrimaryKey()
    """ The primary key of the catalog. """

    entity = ds.Column(ds.String(255), nullable=False)
    """ The settings entity name. """

    user_id = ds.Column(ds.UUID(), ds.ForeignKey('systemUser.id', ondelete='CASCADE'), nullable=True)
    """ The :py:prop:`~wefram.models.User.id` - `id` of the corresponding ``systemUser``
    object for which this catalog is personalized for; if is set to ``None`` - the
    catalog represents as the global scoped. """

    data = ds.Column(ds.JSONB())
    """ The settings catalog's data. Stores actual values for the entity's
    properties. """

    _entity_user_index = ds.Index('systemStoredSettings_entity_user_id', entity, user_id)

