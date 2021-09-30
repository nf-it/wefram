import datetime
from typing import *
import inspect
import decimal
from dataclasses import dataclass
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import Column, Table, select, delete, and_, or_, cast, text
from sqlalchemy.sql import Select, Delete, sqltypes
from sqlalchemy.sql.elements import ClauseList, BinaryExpression, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedDict, InstrumentedList, InstrumentedSet
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
import config
from ...runtime import context
from ...tools import CSTYLE, get_calling_app, snakecase_to_lowercamelcase
from ... import logger
from .types import Attribute


__all__ = [
    'Model',
    'History',
    'app_models',
    'models_by_name',
    'models_by_modulename',
    'models_by_tablename',
    'get_model',
    'tablename_of'
]


app_models = dict()
models_by_name = dict()
models_by_modulename = dict()
models_by_tablename = dict()


class _ModelMetaclass(DeclarativeMeta):
    def __init__(cls, name, bases, clsdict):
        tablename: Optional[str] = None

        app_name: Optional[str] = cls.__modelapp__()
        if not app_name:
            super().__init__(name, bases, clsdict)
            return

        if app_name:
            tablename = cls.__inittablename__(app_name)

        if app_name:
            cls.__decl_cls_name__ = name
            name = tablename
            cls.__name__ = name

        super().__init__(name, bases, clsdict)
        if not app_name:
            return

        meta: Meta = Meta(cls, app_name, cls.__module__)
        for key, attr in cls.__dict__.items():
            if isinstance(attr, Column):
                meta.columns.append(attr)

            if isinstance(attr, Attribute):
                meta.attributes.append(attr)
                attr.parent_class = cls
                attr.parent_key = key

        cls.Meta = meta
        if app_name not in app_models:
            app_models[app_name] = dict()
        app_models[app_name][cls.__decl_cls_name__] = cls
        models_by_name['.'.join([app_name, cls.__decl_cls_name__])] = cls
        models_by_modulename['.'.join([cls.__module__, cls.__decl_cls_name__])] = cls
        models_by_tablename[tablename] = cls

        cls.__app__ = app_name

        logger.debug(
            f"registered ds.Model [{CSTYLE['red']}{name}=`{tablename}`{CSTYLE['clear']}]",
            'ds'
        )

    def __modelapp__(cls) -> Optional[str]:
        mro = cls.mro()
        if len(mro) < 2:
            return None
        delc_app: Optional[str] = getattr(cls, '__app__', None)
        if delc_app:
            return delc_app
        clspath: str = '.'.join([cls.__module__, cls.__name__])
        if clspath in ('sqlalchemy.orm.decl_api.Base', f'{config.COREDIR}.ds.orm.model.Base'):
            return None
        if (not clspath.startswith('ds.orm.history.') and not clspath.startswith(f'{config.COREDIR}.ds.orm.history.')) \
                and (clspath.startswith('ds.') or clspath.startswith(f'{config.COREDIR}.ds.')):
            return None
        if clspath.startswith(f'{config.APPSDIR}.'):
            clspath = '.'.join(clspath.split('.')[1:])
        return clspath.split('.')[0]

    def __inittablename__(cls, app_name: str) -> str:
        tablename: [str, None] = getattr(cls, '__tablename__', None) \
            or getattr(cls, 'table', None)

        if not tablename:
            tablename = ''.join([app_name, cls.__name__])

        setattr(cls, '__tablename__', tablename)

        return tablename


class _Model:
    Meta: 'Meta'

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        table_name: str = getattr(self.__class__, '__tablename__', '?')

        module_name: Optional[str] = self.__metaattr__('module_name', None)
        repr_by: Optional[Sequence[str]] = self.__metaattr__('repr_by', None)
        if repr_by and not isinstance(repr_by, (list, tuple)):
            raise TypeError('Model.Meta.repr_by must be sequence of (str) type!')

        if repr_by:
            reprstr: str = ' '.join([
                f"{k}='{getattr(self, k, None)}'"
                for k in repr_by
            ])
        else:
            reprstr: str = str(self.__pk__)

        module_name = '' if not module_name else f"{module_name}."
        return f"{module_name}{cls_name}<\"{table_name}\"> {reprstr}"

    @classmethod
    def __metaattr__(cls, attr_name: str, default_value: Any = None) -> Any:
        _meta: ClassVar = getattr(cls, 'Meta', None)
        return getattr(_meta, attr_name, default_value) \
            if _meta is not None \
            else default_value

    @classmethod
    async def create(cls, *args, **kwargs):
        db = context['db']
        columns: Dict[str, Column] = cls.Meta.get_columns_dict()
        initial_values = {
            k: v for k, v in cls.Meta.casted_values(**kwargs).items()
            if k in columns
        }

        o: object = cls(*args, **initial_values)
        db.add(o)

        relationship_attrs: List[str] = []
        for k in kwargs:
            c: Optional[Column] = getattr(cls, k, None)
            if c is None:
                continue
            if not hasattr(c, 'prop'):
                continue
            if isinstance(c.prop, RelationshipProperty) and getattr(c.prop, 'uselist', False):
                relationship_attrs.append(k)

        # If there are related values depending on the instance's key - have to flush
        # the instance and only after that apply those values.
        if len([
            k for k in relationship_attrs
            if k in kwargs and isinstance(kwargs[k], (list, tuple, set)) and len(kwargs[k])
        ]):
            await db.flush()
            await db.refresh(o)
            for k in relationship_attrs:
                await (getattr(o, '_update_relationship_value'))(k, kwargs[k])

        return o

    async def delete(self) -> None:
        context['db'].delete(self)

    @classmethod
    async def select(cls, *filter_args, **kw):
        limit: Optional[int] = kw.pop('limit', None)
        offset: Optional[int] = kw.pop('offset', None)
        order: Optional[Union[Any, List[Any]]] = kw.pop('order', None)
        for_update: bool = bool(kw.pop('update', False))

        session: AsyncSession = context['db']
        statement: Select = select(cls)
        if filter_args:
            statement = statement.filter(and_(*filter_args))
        if kw:
            statement = statement.filter_by(**cls.Meta.casted_values(**kw))

        if limit:
            statement = statement.limit(limit)
        if offset:
            statement = statement.offset(limit)

        if order is None and cls.Meta.order:
            order = cls.Meta.get_defalt_order()
        if order is not None and not isinstance(order, (list, tuple)):
            order = [order, ]
        if order is not None:
            statement = statement.order_by(*order)

        if for_update:
            statement = statement.with_for_update()

        return (await session.execute(statement)).scalars()

    async def _update_relationship_value(self, key: str, value: Any):
        c: Optional[Column] = getattr(self.__class__, key, None)
        if not isinstance(value, (list, tuple)):
            raise ValueError("relationship attribute must be set using array value!")
        session: AsyncSession = context['db']
        value: [list, tuple]
        related_table: Table = c.prop.target
        related_tablename: str = related_table.name
        related_model: Optional[ClassVar[Model]] = get_model(related_tablename)
        related_meta: Meta = related_model.Meta
        new_ks = [
            related_meta.pk_as_dict(e) if not isinstance(e, Model) else e.__pk__
            for e in value
        ]
        relattr = getattr(self, key)
        for o in list(relattr):
            _pk = o.__pk__
            if _pk in new_ks:
                new_ks.remove(_pk)
                continue
            relattr.remove(o)
        if new_ks:
            left_objs_clause: List[ClauseList] = or_(*[
                related_meta.primary_key_clause(_pk) for _pk in new_ks
            ])
            left_objs = (await session.execute(select(related_model).where(left_objs_clause))).scalars().all()
            [relattr.append(o) for o in left_objs]

    async def _update(self, key: str, value: Any) -> None:
        c: Optional[Column] = getattr(self.__class__, key, None)
        if c is None:
            # setattr(self, key, value)
            return
        if isinstance(c.prop, RelationshipProperty) and getattr(c.prop, 'uselist', False):
            await self._update_relationship_value(key, value)
            return
        if not isinstance(c, InstrumentedAttribute):
            return
        setattr(self, key, self.Meta.casted_value(c, value))

    async def update(self, **values) -> None:
        [await self._update(k, v) for k, v in values.items()]

    @classmethod
    async def all(cls, *filter_args, **kw):
        return (await cls.select(*filter_args, **kw)).all()

    @classmethod
    async def first(cls, *filter_args, **kw):
        kw['limit'] = 1
        return (await cls.select(*filter_args, **kw)).first()

    @classmethod
    async def get(cls, *pk, update: bool = False):
        return await cls.first(*[
            (c == cls.Meta.casted_value(c, pk[i]))
            for i, c in enumerate(cls.Meta.primary_key)
        ], update=update)

    @classmethod
    async def delete_where(cls, *filter_args, **filter_kwargs):
        session: AsyncSession = context['db']
        statement: Delete = delete(getattr(cls, '__table__'))
        where: list = list(filter_args)
        if filter_kwargs:
            for k in filter_kwargs:
                c = getattr(cls, k, None)
                if c is None:
                    raise LookupError
                where.append(c == filter_kwargs[k])
        if len(where) > 1:
            where: ClauseList = and_(*where)
        elif len(where) == 1:
            where: Any = where[0]
        else:
            where: Any = None
        if where is not None:
            statement = statement.where(where)
        return await session.execute(statement)

    @property
    def __keycaption__(self) -> Tuple[Any, str]:
        return self.__pk1__, self.__caption__

    @property
    def __caption__(self) -> str:
        caption_key: Optional[str] = self.__metaattr__('caption_key')
        if not caption_key:
            return self.__repr__()
        return getattr(self, caption_key, self.__repr__())

    @property
    def key(self) -> Union[Any, Dict[str, Any]]:
        """ Returns the this model instance's primary key.

        Returns a plain value if the primary key is simple (one column), or a dict
        contains columns' names and corresponding values if the model has a complex
        primary key (two or more columns in the primary key constraint).
        """
        value: dict = self.__pk__
        return value if len(value) > 1 else value.popitem()[1]

    @classmethod
    def like(cls, term: str) -> Optional[List[Union[BinaryExpression, UnaryExpression]]]:
        findable_attrs: Sequence[str] = cls.Meta.findable
        if not findable_attrs:
            return None
        clause: List[Union[BinaryExpression, UnaryExpression]] = []
        for name in findable_attrs:
            c: Column = getattr(cls, name)
            clause.append(cast(c, sqltypes.VARCHAR).like(f"%{term}%"))
        return or_(*clause)

    @classmethod
    def ilike(cls, term: str) -> Optional[List[Union[BinaryExpression, UnaryExpression]]]:
        findable_attrs: Sequence[str] = cls.Meta.findable
        if not findable_attrs:
            return None
        clause: List[Union[BinaryExpression, UnaryExpression]] = []
        for name in findable_attrs:
            c: Column = getattr(cls, name)
            clause.append(cast(c, sqltypes.VARCHAR).ilike(f"%{term}%"))
        return or_(*clause)

    @property
    def __pk__(self) -> Dict[str, Any]:
        """ Returns a dict containing the model instance's primary key column names and
        corresponding values. Always returns a dict even if simple primary key
        constraint is defined.
        """
        return {c.name: getattr(self, c.name, None) for c in self.Meta.primary_key}

    @property
    def __pk1__(self) -> Any:
        """ Always returns a single primary key value. If there is a simple primary key
        constraint defined for the model - the simple plain value will be returned. Otherwise,
        the complex primary key value will be returned as a (str) joined using '&' symbol,
        sorted by key name.
        For example, if the primary key constraint is (id1, id2) and, for example, if the
        model instance has id1=100, id2=10, then the result will be "100&10".
        """
        pk: Any = self.key
        if isinstance(pk, dict):
            pk = '&'.join([str(pk[k]) for k in sorted(pk.keys())])
        return pk

    def _attr_for_dict(
            self,
            name: str,
            value: Any,
            deep: bool = False,
            jsonify_names: bool = False,
            fq_urls: bool = True
    ) -> Any:
        from .storage import StoredImage, StoredFile

        if isinstance(value, Model):
            return value.as_dict(jsonify_names=jsonify_names) if deep else value.key
        if isinstance(value, InstrumentedList):
            return [self._attr_for_dict(..., _e, deep, jsonify_names) for _e in value]
        if isinstance(value, InstrumentedDict):
            return {_n: self._attr_for_dict(_n, _e, deep, jsonify_names) for _n, _e in value.items()}
        if isinstance(value, InstrumentedSet):
            return {self._attr_for_dict(..., _e, deep, jsonify_names) for _e in value}
        if isinstance(value, StoredFile):
            return value.url if fq_urls else value.file_id
        return value

    def as_dict(
            self,
            attributes: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            deep: Optional[Union[bool, List[str]]] = False,
            set_name: Optional[str] = None,
            jsonify_names: bool = False,
            fq_urls: bool = True,
            for_history: bool = False
    ) -> Dict[str, Any]:
        def _name(_srcname: str) -> str:
            return _srcname if not jsonify_names else snakecase_to_lowercamelcase(_srcname)

        def _is_key_for_include(__k: str) -> bool:
            if __k.startswith('_'):
                return False
            column_type: Any = self.Meta.column_type(__k)
            if for_history and column_type is None:
                return False
            return True

        def _keys_for_result(_vdkeys: KeysView[str]) -> Sequence[str]:
            if attributes:
                return attributes
            if keys_set:
                return keys_set
            _keys: List[str] = [_k for _k in _vdkeys if _is_key_for_include(_k)]
            _include: Optional[List[str]] = self.__metaattr__('include')
            if _include is not None and not isinstance(_include, (list, tuple)):
                if not isinstance(_include, str):
                    raise TypeError(
                        "Model.Meta.include must be list of (str) attributes names"
                    )
                _include = [_include, ]
            if _include:
                _keys.extend(_include)
            return _keys

        excluding: List[str] = self.__metaattr__('hidden') or []

        if set_name:
            attributes_sets: Dict[str, List[str]] = self.__metaattr__('attributes_sets') or {}

            if not isinstance(attributes_sets, dict):
                raise TypeError("ds.Model.Meta.attributes_sets must be [dict] type")

            if set_name not in attributes_sets:
                raise KeyError(f"set_name {set_name} has not defined in the Model.Meta")
            keys_set: Union[dict, list, tuple] = attributes_sets[set_name]
            keys_set: Sequence[str] = keys_set.keys() if isinstance(keys_set, dict) else keys_set
        else:
            keys_set: None = None

        if not isinstance(excluding, (list, tuple)):
            raise TypeError("ds.Model.Meta.hidden must be [list] of [str] type")

        if exclude and isinstance(exclude, (list, tuple, set)):
            excluding.extend(list(exclude))
        elif exclude:
            raise TypeError("exclude must be [list] of [str] type")

        values_dict = self.__dict__
        keys = _keys_for_result(values_dict.keys())

        result: Dict[str, Any] = dict()
        for k in [k for k in keys if k not in excluding]:
            if k in values_dict:
                v = values_dict.get(k, None)
            elif hasattr(self, k):
                v = getattr(self, k)
            else:
                v = None
            dk = _name(k)
            result[dk] = self._attr_for_dict(k, v, deep, jsonify_names, fq_urls)

        return result

    def as_json(
            self,
            attributes: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            set_name: Optional[str] = None,
            deep: Optional[Union[bool, List[str]]] = False,
    ) -> Dict[str, Any]:
        return self.as_dict(
            attributes=attributes,
            exclude=exclude,
            deep=deep,
            set_name=set_name,
            jsonify_names=True,
            fq_urls=False
        )


Model = declarative_base(cls=_Model, metaclass=_ModelMetaclass)


@dataclass
class History:
    enable: bool = False
    model: ClassVar = None
    ignore: List[Union[str, Column]] = None
    attributes: List[Union[str, Column]] = None
    exclude: List[Union[str, Column]] = None


class Meta:
    """ The model's subclass describing some optionals and service methods for the ORM class.

    Attributes:
        model:
            the class of the corresponding ORM model
        module_name:
            (str) the name of the module where this model is declared at
        app_name:
            (str) the name of the app where this model is declared at
        attributes:
            the array of model attributes
        columns:
            the array of model columns
        caption:
            statically set caption of the model
        caption_plural:
            statically set caption of the model instance when speaking about
            several instances (two or more)
        caption_key:
            (str) the attribute name which about to be user as caption of the
            model instance, if applicable
        hidden:
            the array of model attributes whose will not be included in the
            resulting dict, generated by `as_dict` or `as_json` methods
        include:
            the array of model attributes whose normally not about to be
            included in the resulting dict, generated by `as_dict` or
            `as_json`, but has to be
        attributes_sets:
            (dict) of sets of attributes, useful when need to return only
            specific attributes of the model in the resuling dict, generated
            by `as_dict` or `as_json` methods, formed as set name and
            corresponding list of the set attributes
        repr_by:
            the list of attribute names used to (repr) the model instance,
            which may help programmer to identify the object as the
            specific instance; for example, default repr with set `repr_by`
            to ['id', 'name'] will result in something like:
            <MyModel id=1 name=My name>
        findable:
            the list of attribute names used to find by a textual term
        order:
            the default sorting rule, in the format used by SQLAclhemy
            with default 'sort'
        history:
            (History)

    """

    def __init__(self, cls: _ModelMetaclass, app_name: str, module_name: str):
        self.model: ClassVar = cls
        self.module_name: str = module_name
        self.app_name: str = app_name
        self.caption: str = self.model.__name__
        self.caption_plural: str = self.model.__name__
        self.caption_key: Optional[str] = None
        self.hidden: Optional[List[str]] = None
        self.include: Optional[List[str]] = None
        self.attributes: list = []
        self.columns: list = []
        self.attributes_sets: Optional[Dict[str, Sequence[str]]] = None
        self.repr_by: Optional[List[str]] = None
        self.findable: Optional[List[str]] = None
        self.order: Optional[Union[str, List[str], Column, List[Column]]] = None
        self.history: History = History()

        meta: Optional[dict, ClassVar] = getattr(cls, 'Meta', None)
        if meta:
            if isinstance(meta, dict):
                for k, v in meta:
                    self._instantiate_attribute(k, v)
            elif inspect.isclass(meta):
                for k in dir(meta):
                    if k.startswith('_') or k.endswith('__'):
                        continue
                    self._instantiate_attribute(k, getattr(meta, k))

        if self.findable and not isinstance(self.findable, (list, tuple)):
            raise TypeError(
                f"Model.Meta.findable must be type of (list|tuple)"
                f" of str, {type(self.findable)} given instead"
            )

    def _instantiate_attribute(self, key: str, value: Any) -> None:
        if key == 'history':
            if value is True:
                self.history.enable = True
                return
        setattr(self, key, value)

    @property
    def primary_key(self) -> Sequence[Column]:
        return sa_inspect(self.model).primary_key

    def primary_key_clause(self, pk_values: Dict[str, Any]) -> ClauseList:
        return and_(*[
            getattr(self.model, k) == self.casted_value(getattr(self.model, k), v)
            for k, v in pk_values.items()
        ])

    def column_type(self, attr: Union[str, Column]) -> Any:
        c: InstrumentedAttribute = getattr(self.model, attr, None) \
            if isinstance(attr, str) \
            else attr
        if c is None:
            return None
        try:
            t = c.type
        except AttributeError:
            return None
        if not hasattr(t, 'impl'):
            return t
        if t.impl is not None:
            return t.impl
        return t

    def casted_values(self, **values):
        return {
            k: self.casted_value(getattr(self.model, k, None), v) for k, v in values.items()
        }

    def casted_value(self, c: Optional[Column], v: Any) -> Any:
        if c is None:
            return v
        c_type = self.column_type(c)
        if c_type is None:
            return v
        if isinstance(c_type, sqltypes.String):
            return str(v)
        elif isinstance(c_type, sqltypes.Integer):
            return int(v)
        elif isinstance(c_type, sqltypes.Float):
            return float(v)
        elif isinstance(c_type, sqltypes.Numeric):
            return decimal.Decimal(v)
        elif isinstance(c_type, sqltypes.DateTime):
            if isinstance(v, str):
                return datetime.datetime.fromisoformat(v)
            return v
        elif isinstance(c_type, sqltypes.Date):
            if isinstance(v, str):
                return datetime.date.fromisoformat(v)
            return v
        elif isinstance(c_type, sqltypes.Time):
            if isinstance(v, str):
                return datetime.time.fromisoformat(v)
            return v
        elif isinstance(c_type, sqltypes.LargeBinary):
            return bytes(v.encode())
        return v

    def pk_as_dict(self, value: [str, int, dict]) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        value = list(value) if isinstance(value, (list, tuple)) else [value, ]
        pk = self.primary_key
        if len(pk) != len(value):
            raise ValueError("lengths of given values set and primary key does not matches")
        return {c.name: value[i] for i, c in enumerate(pk)}

    def get_defalt_order(self) -> Optional[List[Union[str, Column]]]:
        if not self.order:
            return None
        order: List[Union[str, Column]] = list(self.order) \
            if isinstance(self.order, (list, tuple, set)) \
            else [self.order, ]
        res: List[Union[str, Column]] = []
        for c in order:
            if isinstance(c, str):
                if c.startswith('-'):
                    c: str = c[1:]
                    column: Optional[Any] = getattr(self.model, c, None)
                    if column is None or not isinstance(column, (Column, InstrumentedAttribute)):
                        res.append(text(' '.join([c, 'desc'])))
                    else:
                        res.append(column.desc())
                else:
                    if c.startswith('+'):
                        c = c[1:]
                    column: Optional[Any] = getattr(self.model, c, None)
                    if column is None or not isinstance(column, (Column, InstrumentedAttribute)):
                        res.append(c)
                    else:
                        res.append(column)
            else:
                res.append(c)
        return res

    def get_columns_list(self) -> List[Column]:
        return list(sa_inspect(self.model).columns)

    def get_columns_dict(self) -> Dict[str, Column]:
        return {c.name: c for c in sa_inspect(self.model).columns}


def get_model(name: str, app_name: str = None) -> [None, ClassVar[Model]]:
    if name in models_by_tablename:
        return models_by_tablename[name]

    if '.' in name and name in models_by_modulename:
        return models_by_modulename[name]

    if '.' in name:
        app_name, name = name.split('.', 2)
    if not app_name:
        app_name = get_calling_app()

    if app_name in app_models and name in app_models[app_name]:
        return app_models[app_name][name]

    for app_name in app_models:
        if name not in app_models[app_name]:
            continue
        return app_models[app_name][name]

    return None


def tablename_of(model: [str, ClassVar[Model]]) -> (str, None):
    if isinstance(model, str):
        model: ClassVar[Model] = get_model(model)
        if model is None:
            return None
        return model.__tablename__
    elif inspect.isclass(model) and issubclass(model, Model):
        return model.__tablename__
    raise ValueError("ds.tablename_of expects model to be given as (str) name or model class")
