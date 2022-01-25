"""
Provides a special case of Entity API realizing the API interfaces for ORM Models.
This gives a simple approach on how to declare API/REST-API for any declared ORM
model without re-writing the same code for every model on common operations
like create, read, update & delete.
"""

from typing import *
from sqlalchemy.sql import Select, select
from sqlalchemy.sql.elements import (
    BinaryExpression,
    UnaryExpression,
    ClauseList,
    ClauseElement)
from sqlalchemy import sql, and_, or_, Column, INT, BIGINT, Integer, BigInteger
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.exc import IntegrityError
from .. import ds, logger, exceptions
from ..ds import db, clause_eq_for_c, Model
from ..l10n import gettext
from ..tools import camelcase_to_snakecase
from .entities import EntityAPI


__all__ = [
    'ModelAPI'
]


class ModelAPI(EntityAPI):
    """ The special case of the EntityAPI class, implementing the ORM model
    CRUD operations. This simplificates the API creation for ORM models,
    realizes corresponding, routed handlers for common operations.

    Notice that there is a good idea to override some methods on this
    basic model if there is a need to make more complex behaviour on the
    one or the another operation.

    For example, let's assume that we have a some extra operations which
    must be done AFTER the object been successfully deleted. Let's make
    a simple example on that:

    .. highlight:: python
    .. code-block:: python

        class MyModel(ModelAPI):
            model = mymodels.MyModel

            async def delete(self, *keys: Union[str, int]) -> None:
                await super().delete(*keys)

                # There are no exceptions raised, so we know that deletion
                # was successful, and do some extra work here.
                print("Funny, its works!")

    """

    model: ClassVar[Model]
    """ The corresponding ORM model class for which this API is declaring for. """

    set_name: Optional[str] = None
    """ Optional name of the ``Model.Meta.attributes_sets`` entry, which will be
    used for read operations. """

    return_created_id: bool = False
    """ If set to ``True`` - the **create** operation will return an object key
    to the frontend on object create done with HTTP result code 200; otherwise
    only Success code 204 (No response) will be returned, indicating the successful
    creation.
    
    This might be useful especially when using auto-increment keys and there is
    a need to know the created object's key after it creation.
    
    Default is ``False``.
    """

    default_deep: bool = False
    """ The API has two behaviours on how to return objects' structs - simple and
    deep. The difference is that in deep behaviour dependend objects (for example,
    joined using Many-to-One, Many-to-Many, One-to-Many, One-to-One relationships)
    will be fetched from the database too and their first-line representations
    will be JSONified and returned to the caller too. See
    :meth:`~wefram.ds.model.Model.dict` of the
    :class:`wefram.ds.model.Model` class for more details.
    
    This behaviour controlled by passing URL argument ``deep=true`` or 
    ``deep=false`` (or even omitting this argument). So, when the argument is
    omitted, the default behaviour, which is controlled by *this* attribute,
    will be used.
    
    Default is ``False``.
    """

    @classmethod
    def path_base(cls) -> str:
        """ Overrides the default entity-API path base to the model original name
        (because the class name rewrites by the ORM mechanics).
        """
        return cls.model.__decl_cls_name__

    @property
    def key_clause(self) -> Optional[ClauseList]:
        """ Returns a ready to use in the query key clause for the corresponding,
        declared by ``model`` ORM model and this instance. Ready to be used in the
        WHERE clause by the ORM mechanics.
        """

        # The `self.key` about to be filled on the instance creating to the
        # instance key. If not - return None.
        if self.key is None:
            return None

        key = self.key
        clause: List[Union[BinaryExpression, UnaryExpression]] = []

        # If the key is a complex one and is an array of values
        if isinstance(key, (list, tuple, set)):
            [clause.append(c == key[i]) for i, c in enumerate(self.model.Meta.primary_key)]

        # If the key is a complex one and formed as dict, where keys are
        # column names and according dict values are columns' values.
        elif isinstance(key, dict):
            for k, v in key.items():
                c: Column = getattr(self.model, k)
                clause.append(c == v)

        # Else, if the key is a simple one (most often case)
        else:
            c: Column = self.model.Meta.primary_key[0]
            clause.append(c == key)

        # Return AND-joined clause
        return and_(*clause)

    def keys_clause(self, keys: List[Union[str, int]]) -> Optional[ClauseElement]:
        """ Returns a ready to use in the query key clause for the corresponding,
        declared by ``model`` ORM model and given list of *SIMPLE* keys.
        Ready to be used in the WHERE clause by the ORM mechanics.

        Please note that this method does not work with complex keys!

        :param keys:
            A list of simple keys (str or int type).

        :return:
            A ready to use in the query SQLAlchemy clause, based on *IN*
            database operator.
        """

        if not keys:
            return None
        c: Column = self.model.Meta.primary_key[0]
        if isinstance(c.type, (Integer, BigInteger, INT, BIGINT)):
            keys = [int(k) for k in keys]
        else:
            keys = [str(k) for k in keys]
        return c.in_(keys)

    @classmethod
    async def create(cls, **with_values) -> Union[bool, object]:
        """ Creates a new ORM model instance, filling up it with the given in the
        payload values, saving it to the database.

        Note that this method calls :py:func:`flush` function of the database
        session to ensure successful operation and handle some special case
        errors like integrity errors.
        """

        with_values: dict = {
            k: v for k, v in {
                k: await cls.encode_value(k, v) for k, v in with_values.items()
            }.items() if v is not ...
        }
        instance: Model = await cls.model.create(**with_values)
        try:
            await db.flush()
        except IntegrityError as e:
            logger.debug(str(e.orig))
            raise exceptions.DatabaseIntegrityError()
        return instance.key if cls.return_created_id else True

    def handle_read_filter(self, c: QueryableAttribute, value: Any) -> Optional[ClauseElement]:
        """ Used by the class mechanics to handle passed in the URL argument filter and
        return an SQLAlchemy ready to use clause.

        :param c:
            The corresponding ORM Model attribute (column) for which to handle filter for;

        :param value:
            The raw value which about to be handled.

        :return:
            SQLAlchemy ready to use clause
        """

        if isinstance(value, str) and ')||(' in value and value.startswith('(') and value.endswith(')'):
            values: List[str] = value[1:-1].split(')||(')
            clauses: List[ClauseElement] = [
                clause_eq_for_c(c, value) for value in values
            ]
            return or_(*clauses)
        return clause_eq_for_c(c, value)

    async def filter_read(
            self,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            **filters: Any
    ) -> ClauseList:
        """ Returns ready to use SQLAlchemy filter clause basing on the given filters for the
        read CRUD operation.

        There are two basic filtering handling by this method:

        * *value filtering* - filter model objects by some value (some defined model column);
        * *search* - try to find objects by ``search`` operation (for more details see
            :py:meth:`~ds.model.Model.like` and :py:meth:`~ds.model.Model.ilike`). Search operation
            may be, according to corresponding methods of the :py:class:`~ds.model.Model` class -
            ``like`` (strict, case sensetive search) and ``ilike`` (case insensetive search).

        Filters expected to be specified using URL arguments. For example:

        ``[GET] /api/myapp/MyModel?name=John&lastName=Final``

        or

        ``[GET] /api/myapp/MyModel?ilike=eugene``

        Note that standard Wefram frontend functionality takes care on how to make the resulting
        URL with or without filters, by using corresponding frontend API methods (TypeScript
        written).
        """

        conditions: List[ClauseElement] = []

        for name, value in filters.items():
            c: QueryableAttribute = getattr(self.model, name, None)
            if c is None or not isinstance(c, QueryableAttribute):
                # If the model has no column with given name - skip this filter
                # raise KeyError(
                #     f"Model '{self.model.__name__}' has no column '{name}' which participates in the ModelAPI filter"
                # )
                continue
            clause: Optional[ClauseElement] = self.handle_read_filter(c, value)
            if clause is None:
                continue
            conditions.append(clause)

        if like:
            conditions.append(self.model.like(like))

        if ilike:
            conditions.append(self.model.ilike(ilike))

        return and_(*conditions)

    async def item_as_json(self, instance: Model, deep: bool = None) -> dict:
        """ Returns the given instance JSONified.

        :param instance:
            The ORM Model instance to JSONify to.
        :type instance:
            Model instance

        :param deep:
            Do the deep JSONify or not. See :meth:`~wefram.ds.model.Model.dict` of the
            :class:`wefram.ds.model.Model` class for more details
        :type deep:
            bool

        :return:
            The JSONify ready Python dict.
        :rtype:
            dict
        """

        return {
            k: await self.decode_value(k, v)
            for k, v in instance.json(
                set_name=self.set_name,
                deep=(deep if isinstance(deep, bool) else self.default_deep)
            ).items()
        }

    async def items_as_json(self, instances: List[Model], deep: bool = None) -> List[dict]:
        """ Returns the given instances JSONified.

        :param instances:
            The ORM Model instances to JSONify to.
        :type instances:
            List of Model instances

        :param deep:
            Do the deep JSONify or not. See :meth:`~wefram.ds.model.Model.dict` of the
            :class:`wefram.ds.model.Model` class for more details
        :type deep:
            bool

        :return:
            The JSONify ready Python dict.
        :rtype:
            List of dicts
        """

        jsoned_items: List[dict] = [
            i.json(
                set_name=self.set_name,
                deep=(deep if isinstance(deep, bool) else self.default_deep)
            ) for i in instances
        ]
        ready_items: List[dict] = []
        for i in jsoned_items:
            ready_items.append({
                k: await self.decode_value(k, v) for k, v in i.items()
            })
        return ready_items

    async def read_single(self, key: Union[str, int], deep: bool = None) -> Dict[str, Any]:
        instance: Optional[Model] = await self.model.get(key)

        # If the entity object has not been found - raise 404
        if instance is None:
            raise exceptions.ObjectNotFoundError()

        # Returning the single entity object
        return await self.item_as_json(instance, deep=deep)

    async def sort(self, **kwargs) -> Optional[Union[Any, List[Any]]]:
        return kwargs.get('order', None)

    async def read_many(
            self,
            keys: List[Union[str, int]],
            count: bool = False,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            order: Optional[Union[str, List[str]]] = None,
            deep: bool = None,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            filters: Optional[Dict[str, Union[str, int, None, Sequence]]] = None
    ) -> [dict, List[dict]]:
        keys: List[str, int]
        keys_clause: Optional[Union[ClauseList, ClauseElement]] = \
            self.key_clause if not keys else self.keys_clause(list(keys))

        order = await self.sort(
            keys=keys,
            count=count,
            offset=offset,
            limit=limit,
            order=order,
            deep=deep,
            like=like,
            ilike=ilike,
            filters=filters
        )
        if order:
            order: List[str] = list(order) if isinstance(order, (list, tuple, set)) else [order, ]
            order = [camelcase_to_snakecase(k) for k in order]
            order_clause: List[str] = [
                (getattr(self.model, k) if not k.startswith('-') else getattr(self.model, k[1:]).desc())
                for k in order
            ]
        else:
            order_clause: List[Union[str, Column, None]] = self.model.Meta.get_defalt_order()

        filter_clause: Optional[ClauseList] = await self.filter_read(
            like=like,
            ilike=ilike,
            **filters
        )

        where_clause: List[ClauseList, ClauseElement] = []
        if keys_clause is not None:
            where_clause.append(keys_clause)
        if filter_clause is not None:
            where_clause.append(filter_clause)

        stmt: Select = select(self.model)
        if where_clause:
            stmt = stmt.where(and_(*where_clause))

        totalcount: int = await db.scalar(stmt.with_only_columns([ds.func.count(self.model.Meta.primary_key[0])])) \
            if count else None

        if offset:
            stmt = stmt.offset(offset)

        if limit:
            stmt = stmt.limit(limit)

        if order_clause:
            stmt = stmt.order_by(*order_clause)

        instances: List[Any] = await db.all(stmt)
        items: List[dict] = await self.items_as_json(instances, deep=deep)

        return items if not count else {
            'itemsCount': totalcount,
            'items': items
        }

    async def read(
            self,
            *keys: Union[str, int],
            count: bool = False,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            order: Optional[Union[str, List[str]]] = None,
            deep: bool = None,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            **filters: Any
    ) -> Union[Model, dict, List[dict]]:
        # If requested the single entity object to be fetched
        if self.key:
            return await self.read_single(self.key, deep=deep)

        # If has been requested a list of entity objects
        return await self.read_many(
            list(keys),
            count=count,
            offset=offset,
            limit=limit,
            order=order,
            deep=deep,
            like=like,
            ilike=ilike,
            filters=filters
        )

    async def options(
            self,
            *keys: Union[str, int],
            like: Optional[str] = None,
            ilike: Optional[str] = None
    ) -> dict:
        keys: List[str, int]
        keys_clause: Optional[Union[ClauseList, ClauseElement]] = \
            self.key_clause if not keys else self.keys_clause(list(keys))
        filter_clause: Optional[ClauseList] = await self.filter_read(
            like=like,
            ilike=ilike
        )

        where_clause: List[ClauseList, ClauseElement] = []
        if keys_clause is not None:
            where_clause.append(keys_clause)
        if filter_clause is not None:
            where_clause.append(filter_clause)

        stmt: Select = select(self.model)
        if where_clause:
            stmt = stmt.where(and_(*where_clause))

        instances: list = await db.all(stmt)
        return {i.__pk1__: i.__caption__ for i in instances}

    async def update(self, *keys: Union[str, int], **values) -> None:
        values: dict = {
            k: v for k, v in {
                k: await self.encode_value(k, v) for k, v in values.items()
            }.items() if v is not ...
        }
        keys: List[str, int]
        clause: [ClauseList, ClauseElement] = self.key_clause if not keys else self.keys_clause(list(keys))
        instances: list = await self.model.all(clause)
        if not instances:
            return

        for instance in instances:
            await instance.update(**values)

        try:
            await db.flush()

        except IntegrityError as e:
            logger.debug(str(e.orig))
            raise exceptions.DatabaseIntegrityError()

    async def delete(self, *keys: Union[str, int]) -> None:
        keys: List[str, int]
        clause: [ClauseList, ClauseElement] = self.key_clause if not keys else self.keys_clause(list(keys))
        stmt = sql.delete(self.model.__table__).where(clause)
        await db.execute(stmt)

        try:
            await db.flush()

        except IntegrityError as e:
            logger.debug(str(e.orig))
            raise exceptions.DatabaseIntegrityError(
                gettext("The object cannot be deleted because others depend on it.", 'wefram.messages')
            )
