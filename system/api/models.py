from typing import *
from sqlalchemy.sql import Select, select
from sqlalchemy.sql.elements import (
    BinaryExpression,
    UnaryExpression,
    ClauseList,
    ClauseElement)
from sqlalchemy import sql, and_, or_, Column
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.exc import IntegrityError
from .. import ds
from ..ds import db, clause_eq_for_c, Model
from ..requests import HTTPException
from ..tools import camelcase_to_snakecase
from .entities import EntityAPI


class ModelAPI(EntityAPI):
    """ The special case of the EntityAPI class, implementing the ORM model
    CRUD operations.
    """

    model: ClassVar[Model] = None
    set_name: Optional[str] = None
    return_created_id: bool = True

    @classmethod
    def path_base(cls) -> str:
        return cls.model.__name__

    @property
    def key_clause(self) -> Optional[ClauseList]:
        if self.key is None:
            return None

        key = self.key
        clause: List[Union[BinaryExpression, UnaryExpression]] = []

        if isinstance(key, (list, tuple, set)):
            [clause.append(c == key[i]) for i, c in enumerate(self.model.Meta.primary_key)]

        elif isinstance(key, dict):
            for k, v in key.items():
                c: Column = getattr(self.model, k)
                clause.append(c == v)

        else:
            c: Column = self.model.Meta.primary_key[0]
            clause.append(c == key)

        return and_(*clause)

    def keys_clause(self, keys: List[Union[str, int]]) -> Optional[ClauseElement]:
        if not keys:
            return None
        c: Column = self.model.Meta.primary_key[0]
        return c.in_(keys)

    @classmethod
    async def create(cls, **with_values) -> Union[bool, object]:
        # with_values: dict = {k: await cls.encode_value(k, v) for k, v in with_values.items()}
        with_values: dict = {
            k: v for k, v in {
                k: await cls.encode_value(k, v) for k, v in with_values.items()
            }.items() if v is not ...
        }
        instance: Model = cls.model.create(**with_values)
        try:
            await db.flush()
        except IntegrityError as e:
            raise HTTPException(400, str(e.orig))
        return instance.pk if cls.return_created_id else True

    def handle_read_filter(self, c: QueryableAttribute, value: Any) -> Optional[ClauseElement]:
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
        conditions: List[ClauseElement] = []

        for name, value in filters.items():
            c: QueryableAttribute = getattr(self.model, name, None)
            if c is None or not isinstance(c, QueryableAttribute):
                # If the model has no column with given name - raise exception
                raise KeyError(
                    f"Model '{self.model.__name__}' has no column '{name}' which participates in the ModelAPI filter"
                )
            clause: Optional[ClauseElement] = self.handle_read_filter(c, value)
            if clause is None:
                continue
            conditions.append(clause)

        if like:
            conditions.append(self.model.like(like))

        if ilike:
            conditions.append(self.model.ilike(ilike))

        return and_(*conditions)

    async def item_as_json(self, instance: Model, deep: bool = False) -> dict:
        return {
            k: await self.decode_value(k, v)
            for k, v in instance.as_json(set_name=self.set_name, deep=deep).items()
        }

    async def items_as_json(self, instances: List[Model], deep: bool = False) -> List[dict]:
        jsoned_items: List[dict] = [i.as_json(set_name=self.set_name, deep=deep) for i in instances]
        ready_items: List[dict] = []
        for i in jsoned_items:
            ready_items.append({
                k: await self.decode_value(k, v) for k, v in i.items()
            })
        return ready_items

    async def read_single(self, key: [str, int], deep: bool = False) -> Dict[str, Any]:
        instance: Optional[Model] = await self.model.get(key)
        # If the entity object has not been found - raise 404
        if instance is None:
            raise HTTPException(404)
        # Returning the single entity object
        return await self.item_as_json(instance, deep=deep)

    async def read_many(
            self,
            keys: List[Union[str, int]],
            count: bool = False,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            order: Optional[Union[str, List[str]]] = None,
            deep: bool = False,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            filters: Optional[Dict[str, Union[str, int, None, Sequence]]] = None
    ) -> [dict, List[dict]]:
        keys: List[str, int]
        keys_clause: Optional[Union[ClauseList, ClauseElement]] = \
            self.key_clause if not keys else self.keys_clause(list(keys))
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

        if order:
            order: List[str] = list(order) if isinstance(order, (list, tuple, set)) else [order, ]
            order = [camelcase_to_snakecase(k) for k in order]
            _order: List[str] = [
                (getattr(self.model, k) if not k.startswith('-') else getattr(self.model, k[1:]).desc())
                for k in order
            ]
            stmt = stmt.order_by(*_order)
        else:
            _order: List[Union[str, Column]] = self.model.Meta.get_defalt_order()

        instances: List[Model] = await db.all(stmt)
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
            deep: bool = False,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            **filters: Any
    ) -> Union[Model, dict, List[dict]]:
        # If requested the single entity object to be fetched
        if self.key:
            return await self.read_single(self.key, deep=deep)

        if keys is None:
            raise HTTPException(400)

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

        instances: List[Model] = await db.all(stmt)
        return {i.__pk1__: i.__caption__ for i in instances}

    async def update(self, *keys: [str, int], **values) -> None:
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
            raise HTTPException(400, str(e.orig))

    async def delete(self, *keys: [str, int]) -> None:
        keys: List[str, int]
        clause: [ClauseList, ClauseElement] = self.key_clause if not keys else self.keys_clause(list(keys))
        stmt = sql.delete(self.model.__table__).where(clause)
        await db.execute(stmt)

        try:
            await db.commit()  # TODO! Is there COMMIT really needed?, or just FLUSH is enought for that

        except IntegrityError as e:
            raise HTTPException(400, str(e.orig))
