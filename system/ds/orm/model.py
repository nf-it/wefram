from typing import *
import inspect
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import Column, Table, select, delete, and_, or_
from sqlalchemy.sql import Select, Delete
from sqlalchemy.sql.elements import ClauseList, BinaryExpression, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedDict, InstrumentedList, InstrumentedSet
from sqlalchemy.orm.relationships import RelationshipProperty
import config
from ...requests import context
from ...tools import CSTYLE, get_calling_app, snakecase_to_lowercamelcase
from ... import logger
from .types import Attribute


__all__ = [
    'Model',
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
        if app_name:
            tablename = cls.__inittablename__(app_name)

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
        app_models[app_name][cls.__name__] = cls
        models_by_name['.'.join([app_name, cls.__name__])] = cls
        models_by_modulename['.'.join([cls.__module__, cls.__name__])] = cls
        models_by_tablename[tablename] = cls

        logger.debug(
            f"registered ds.Model [{CSTYLE['red']}{name}=`{tablename}`{CSTYLE['clear']}]"
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
        if clspath.startswith('ds.') or clspath.startswith(f'{config.COREDIR}.ds.'):
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
    def create(cls, *args, **kwargs):
        o: object = cls(*args, **kwargs)
        context['db'].add(o)
        return o

    async def delete(self) -> None:
        context['db'].delete(self)

    @classmethod
    async def select(cls, *filter_args, **kw):
        limit: Optional[int] = kw.pop('limit', None)
        offset: Optional[int] = kw.pop('offset', None)
        order: Optional[Union[Any, List[Any]]] = kw.pop('order', None)

        session: AsyncSession = context['db']
        statement: Select = select(cls)
        if filter_args:
            statement = statement.filter(and_(*filter_args))
        if kw:
            statement = statement.filter_by(**kw)

        if limit:
            statement = statement.limit(limit)
        if offset:
            statement = statement.offset(limit)

        if order is None and cls.Meta.order:
            order = cls.Meta.order
        if order is not None and not isinstance(order, (list, tuple)):
            order = [order, ]
        if order is not None:
            statement = statement.order_by(*order)

        return (await session.execute(statement)).scalars()

    async def _update(self, key: str, value: Any) -> None:
        c: Optional[Column] = getattr(self.__class__, key, None)
        if c is None:
            setattr(self, key, value)
            return
        if isinstance(c.prop, RelationshipProperty) and getattr(c.prop, 'uselist', False):
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
                [relattr.register(o) for o in left_objs]
            return
        setattr(self, key, value)

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
    async def get(cls, *pk):
        return await cls.first(*[(c == pk[i]) for i, c in enumerate(cls.Meta.primary_key)])

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
        if where:
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
    def pk(self) -> Union[Any, Dict[str, Any]]:
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
            clause.append(c.like(f"%{term}%"))
        return or_(*clause)

    @classmethod
    def ilike(cls, term: str) -> Optional[List[Union[BinaryExpression, UnaryExpression]]]:
        findable_attrs: Sequence[str] = cls.Meta.findable
        if not findable_attrs:
            return None
        clause: List[Union[BinaryExpression, UnaryExpression]] = []
        for name in findable_attrs:
            c: Column = getattr(cls, name)
            clause.append(c.ilike(f"%{term}%"))
        return or_(*clause)

    @property
    def __pk__(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name, None) for c in self.Meta.primary_key}

    @property
    def __pk1__(self) -> Any:
        pk: Any = self.pk
        if isinstance(pk, dict):
            pk = list(pk.keys())[0]
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
            return value.as_dict(jsonify_names=jsonify_names) if deep else value.pk
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
            deep: Optional[Union[bool, List[str]]] = False,
            set_name: Optional[str] = None,
            jsonify_names: bool = False,
            fq_urls: bool = True
    ) -> Dict[str, Any]:
        def _name(_srcname: str) -> str:
            return _srcname if not jsonify_names else snakecase_to_lowercamelcase(_srcname)

        def _keys_for_result(_vdkeys: KeysView[str]) -> Sequence[str]:
            if attributes:
                return attributes
            if keys_set:
                return keys_set
            _keys: List[str] = [_k for _k in _vdkeys if not _k.startswith('_')]
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

        hidden: List[str] = self.__metaattr__('hidden') or []

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

        if not isinstance(hidden, (list, tuple)):
            raise TypeError("ds.Model.Meta.hidden must be [list] of [str] type")

        values_dict = self.__dict__
        keys = _keys_for_result(values_dict.keys())

        result: Dict[str, Any] = dict()
        for k in [k for k in keys if k not in hidden]:
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
            set_name: Optional[str] = None,
            deep: Optional[Union[bool, List[str]]] = False,
    ) -> Dict[str, Any]:
        return self.as_dict(
            attributes=attributes,
            deep=deep,
            set_name=set_name,
            jsonify_names=True,
            fq_urls=False
        )


Model = declarative_base(cls=_Model, metaclass=_ModelMetaclass)


class Meta:
    def __init__(self, cls: _ModelMetaclass, app_name: str, module_name: str):
        """
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
        """
        self.model: ClassVar = cls
        self.module_name: str = module_name
        self.app_name: str = app_name
        self.attributes: List[Attribute] = list()
        self.columns: List[Column] = list()
        self.caption: str = self.model.__name__
        self.caption_plural: str = self.model.__name__
        self.caption_key: Optional[str] = None
        self.hidden: Optional[List[str]] = None
        self.include: Optional[List[str]] = None
        self.attributes_sets: Optional[Dict[str, Sequence[str]]] = None
        self.repr_by: Optional[List[str]] = None
        self.findable: Optional[List[str]] = None
        self.order: Optional[Union[str, List[str], Column, List[Column]]] = None

        meta: Optional[dict, ClassVar] = getattr(cls, 'Meta', None)
        if meta:
            if isinstance(meta, dict):
                for k, v in meta:
                    setattr(self, k, v)
            elif inspect.isclass(meta):
                for k in dir(meta):
                    if k.startswith('_') or k.endswith('__'):
                        continue
                    setattr(self, k, getattr(meta, k))

        if self.findable and not isinstance(self.findable, (list, tuple)):
            raise TypeError(
                f"Model.Meta.findable must be type of (list|tuple)"
                f" of str, {type(self.findable)} given instead"
            )

    @property
    def primary_key(self) -> Sequence[Column]:
        return sa_inspect(self.model).primary_key

    def primary_key_clause(self, pk_values: Dict[str, Any]) -> ClauseList:
        return and_(*[
            getattr(self.model, k) == v for k, v in pk_values.items()
        ])

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
        return list(self.order) \
            if isinstance(self.order, (list, tuple, set)) \
            else [self.order, ]


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
