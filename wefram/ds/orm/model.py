import datetime
import decimal
import inspect
from dataclasses import dataclass
from typing import *

from sqlalchemy import Column, Table, select, delete, and_, or_, cast, text
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.collections import InstrumentedDict, InstrumentedList, InstrumentedSet
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql import Select, Delete, sqltypes
from sqlalchemy.sql.elements import ClauseList, BinaryExpression, UnaryExpression

from . import reg
from .types import Attribute
from ... import config, logger
from ...runtime import context
from ...tools import CSTYLE, snakecase_to_lowercamelcase, app_name

__all__ = [
    'Model',
    'DatabaseModel',
    'Meta',
    'History',
]


class _ModelMetaclass(DeclarativeMeta):
    def __init__(cls, name, bases, clsdict):
        tablename: Optional[str] = None

        app: Optional[str] = cls.__modelapp__()
        if not app:
            super().__init__(name, bases, clsdict)
            return

        if app:
            tablename = cls.__inittablename__(app)

        if app:
            cls.__decl_cls_name__ = name
            name = tablename
            cls.__name__ = name

        super().__init__(name, bases, clsdict)
        if not app:
            return

        meta: Meta = Meta(cls, app, cls.__module__)
        for key, attr in cls.__dict__.items():
            if isinstance(attr, Column):
                meta.columns.append(attr)

            if isinstance(attr, Attribute):
                meta.attributes.append(attr)
                attr.parent_class = cls
                attr.parent_key = key

        cls.Meta = meta
        if app not in reg.app_models:
            reg.app_models[app] = dict()
        reg.app_models[app][cls.__decl_cls_name__] = cls
        reg.models_by_name['.'.join([app, cls.__decl_cls_name__])] = cls
        reg.models_by_modulename['.'.join([cls.__module__, cls.__decl_cls_name__])] = cls
        reg.models_by_tablename[tablename] = cls

        cls.__app__ = app

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
        if clspath in ('sqlalchemy.orm.decl_api.Base', f'{config.COREPKG}.ds.orm.model.Base'):
            return None
        if (not clspath.startswith('ds.orm.history.') and not clspath.startswith(f'{config.COREPKG}.ds.orm.history.')) \
                and (clspath.startswith('ds.') or clspath.startswith(f'{config.COREPKG}.ds.')):
            return None
        return app_name(clspath.split('.')[0])

    def __inittablename__(cls, app: str) -> str:
        tablename: [str, None] = getattr(cls, '__tablename__', None) \
                                 or getattr(cls, 'table', None)

        if not tablename:
            tablename = ''.join([app, cls.__name__])

        setattr(cls, '__tablename__', tablename)

        return tablename


class Model:
    """ The Model class which about to be used to map Python data class to the
    corresponding database table.

    .. important::

        The resulting database table name is not the same as the Python class
        name! The tablename is a merge of the **app** name where the corresponding
        Python class have been declared, and the **class** name itself.

        For example, for the class ``MyModel`` declared within app ``myapp``,
        the resulting table name will be ``myappMyModel``.

        This behavior may be overriden with ``__tablename__`` attribute of the
        Python class:

        .. highlight:: python
        .. code-block:: python

            class MyModel(ds.Model):
                __tablename__ = 'whooshtable'
                ...

    """

    Meta: 'Meta'

    @property
    def __caption__(self) -> str:
        """ Returns a string caption (not the Python representation) of the model object instance.
        It uses :class:`~wefram.ds.orm.model.Meta` class and its corresponding attribute
        :py:attr:`~wefram.ds.orm.model.Meta.caption_key` to identify the column or attribute which
        has the human readable name of the object.

        The ``caption_key`` may be defined in plain in the :class:`~wefram.ds.orm.model.Meta`:

            .. highlight:: python
            .. code-block:: python

            class MyModel(ds.Model):
                id = ds.UUIDPrimaryKey()
                name = ds.Column(ds.String(100), nullable=False, default='')

                class Meta:
                    caption_key = 'name'

        Or it may be set by declaring some attribute as :py:class:`~wefram.ds.orm.types.Caption`:

            .. highlight:: python
            .. code-block:: python

            class MyModel(ds.Model):
                id = ds.UUIDPrimaryKey()
                name = ds.Column(ds.Caption(), nullable=False, default='')

        """

        caption_key: Optional[str] = self.__metaattr__('caption_key')
        if not caption_key:
            return self.__repr__()
        return getattr(self, caption_key, self.__repr__())

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

    @property
    def __keycaption__(self) -> Tuple[Any, str]:
        """ Returns a tuple contains the primary key value & the caption of the
        model object instance.
        """
        return self.__pk1__, self.__caption__

    @classmethod
    def __metaattr__(cls, attr_name: str, default_value: Any = None) -> Any:
        """ Returns a value of the Meta subclass of the model. Or the default value. """

        _meta: ClassVar = getattr(cls, 'Meta', None)
        return getattr(_meta, attr_name, default_value) \
            if _meta is not None \
            else default_value

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
        from .storage import StoredFile

        if isinstance(value, Model):
            return value.dict(jsonify_names=jsonify_names) if deep else value.key
        if isinstance(value, InstrumentedList):
            return [self._attr_for_dict(..., _e, deep, jsonify_names) for _e in value]
        if isinstance(value, InstrumentedDict):
            return {_n: self._attr_for_dict(_n, _e, deep, jsonify_names) for _n, _e in value.items()}
        if isinstance(value, InstrumentedSet):
            return {self._attr_for_dict(..., _e, deep, jsonify_names) for _e in value}
        if isinstance(value, StoredFile):
            return value.url if fq_urls else value.file_id
        return value

    async def _update_relationship_value(self, key: str, value: Any):
        c: Optional[Column] = getattr(self.__class__, key, None)
        if not isinstance(value, (list, tuple)):
            raise ValueError("relationship attribute must be set using array value!")
        session: AsyncSession = context['db']
        value: [list, tuple]
        related_table: Table = c.prop.target
        related_tablename: str = related_table.name
        related_model: Optional[ClassVar[Model]] = reg.get_model(related_tablename)
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

    @classmethod
    async def all(
            cls,
            *clause,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            order: Optional[Union[Any, List[Any]]] = None,
            update: bool = False,
            **filters
    ):
        """ Returns a list of fetched from the database model objects by given criteria.
        The method params have been described in the :py:meth:`~select` method.
        """
        return (await cls.select(*clause, limit=limit, offset=offset, order=order, update=update, **filters)).all()

    @classmethod
    async def create(cls, **initials):
        """ Creates a new object of the model returning it to the caller. The new
        object automatically assignes to the current database session. You may
        set the new object's columns values with needed ones by passing them
        as named arguments (kwargs).

        .. highlight:: python
        .. code-block:: python

            new_object = await MyModel.create(column1='value1', column2='value2')

        """

        db = context['db']
        columns: Dict[str, Column] = cls.Meta.get_columns_dict()
        initial_values = {
            k: v for k, v in cls.Meta.casted_values(**initials).items()
            if k in columns
        }

        o: object = cls(**initial_values)
        db.add(o)

        relationship_attrs: List[str] = []
        for k in initials:
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
            if k in initials and isinstance(initials[k], (list, tuple, set)) and len(initials[k])
        ]):
            await db.flush()
            await db.refresh(o)
            for k in relationship_attrs:
                await (getattr(o, '_update_relationship_value'))(k, initials[k])

        return o

    async def delete(self) -> None:
        """ Removes the object from the database. The object must be fetched prior to removing,
        because the ``delete()`` is a instance-level (not class-level) method. Calls on the
        object which about to be deleted.

        .. highlight:: python
        .. code-block:: python

            instance = await MyModel.get('...')
            ...
            await instance.delete()

        """
        await context['db'].delete(self)

    @classmethod
    async def delete_where(cls, *clause, **filters) -> None:
        """ Removes object(s) from the database with direct ``delete`` request to the DB.
        This method does not loads corresponding objects from the DB prior to delete,
        instead it operates with given clause and filters.

        :param clause:
            A list of filtering clause (``WHERE`` clause) as SQLAlchemy expression. If more
            than one argument be given - them all will be grouped by ``AND`` expression.

        :param filters:
            For the simplier case, when filtering with ``AND`` clause only, you may use
            named arguments to indicate whose objects/rows to fetch. For example:

            .. highlight:: python
            .. code-block:: python

                # Lets delete all rows where sold=True AND closed=True
                await MyModel.delete_where(sold=True, closed=True)

        .. attention::

            This method will not trigger history logging of deleting objects because it
            not load the corresponding objects prior to execute. So it is not a best
            idea to use it on logged objects.

        """
        session: AsyncSession = context['db']
        statement: Delete = delete(getattr(cls, '__table__'))
        where: list = list(clause)
        if filters:
            for k in filters:
                c = getattr(cls, k, None)
                if c is None:
                    raise LookupError
                where.append(c == filters[k])
        if len(where) > 1:
            where: ClauseList = and_(*where)
        elif len(where) == 1:
            where: Any = where[0]
        else:
            where: Any = None
        if where is not None:
            statement = statement.where(where)
        return await session.execute(statement)

    def dict(
            self,
            attributes: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            deep: Optional[Union[bool, List[str]]] = False,
            set_name: Optional[str] = None,
            jsonify_names: bool = False,
            for_jsonify: bool = False,
            fq_urls: bool = True
    ) -> Dict[str, Any]:
        """ Returns a python dict type representation of the model object instance. Is very
        useful when you need to deal not with real values and attributes of the model object,
        but in some case - with the dict, which contains the model columns as keys and
        corresponding values.

        By default, only :py:class:`~wefram.ds.orm.Column` type attributes will be
        included into resulting dict, excluding any declared additional model's properties,
        non-column attributes and etc. This behavior may be changed by ``attributes``,
        ``exclude``, and ``set_name`` params (see params explanation).

        :param attributes:
            A list of attributes whose to include into the resulting dict. May be useful
            when you need to include attributes whose are not columns, or exclude some
            attributes at all.
        :type attributes:
            optional, list

        :param exclude:
            A list of column attributes whose must be excluded from the dict.
        :type exclude:
            optional, list

        :param deep:
            If set to ``True`` - the relationship-based attributes will be returned as
            dicts too (will be unpacked as sub-dict); otherwise only primary key(s)
            will be returned as a value for the relationship-based attributes.

            For example:

                .. highlight:: python
                .. code-block:: python

                    my_model_obj.dict(deep=False)
                    # Will result as:
                    # {
                    #   'id': 1005,
                    #   'name': 'Mike',
                    #   'phones': [19432, 95123]  # the related objects ids
                    # }

                    my_model_obj.dict(deep=True)
                    # Will result as:
                    # {
                    #   'id': 1005,
                    #   'name': 'Mike',
                    #   'phones': [
                    #       {
                    #           'id': 19432',
                    #           'phone_type': 'personal',
                    #           'value': '+70001110011'
                    #       },
                    #       {
                    #           'id': 95123',
                    #           'phone_type': 'work',
                    #           'value': '1234'
                    #       }
                    #   ]
                    # }

        :type deep:
            bool, default = False

        :param set_name:
            The name of the attributes set (see :py:attr:`wefram.ds.orm.model.Meta.attributes_sets`
            attribute of the :class:`~wefram.ds.orm.model.Meta` class for explanation)
        :type set_name:
            optional, str

        :param jsonify_names:
            If set to ``True``, the dict keys will have JSON-corrected names. This means that
            Pythonic ``snake_case`` names will be transformed to more JS/JSON usual
            ``lowerCamelCase``.
        :type jsonify_names:
            bool, default = False

        :param for_jsonify:
            If set to ``True`` - the resulting dict will consist of only JSONifying keys
            and values.
        :type for_jsonify:
            bool, default = False

        :param fq_urls:
            If set to ``True``, the :class:`~wefram.ds.orm.types.File` and
            :class:`~wefram.ds.orm.types.Image` columns will result with fully-qualified
            URLs instead or relative ones.
        :type fq_urls:
            bool, default = True

        :return:
            The resulting dict containing the attributes' keys and corresponding values
        :rtype:
            dict
        """

        def _name(_srcname: str) -> str:
            return _srcname if not jsonify_names else snakecase_to_lowercamelcase(_srcname)

        def _is_key_for_include(__k: str) -> bool:
            if __k.startswith('_'):
                return False
            column_type: Any = self.Meta.column_type(__k)
            if for_jsonify and column_type is None:
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
        excluding = list(excluding)

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

    @classmethod
    async def fetch(cls, *pks, update: bool = False):
        """ Returns a list of objects by their primary key values. Like the
        :py:meth:`~get` method, but queries for several
        objects at a time.

        :param pks:
            The list of primary keys of the model objects about to be fetched.
            It the model has complex primary key declared - the every primary
            key must be formed as tuple, consisting of corresponding values
            in the order they been declared in the model.
        :type pks:
            list of keys, or list of tuples of keys

        :param update:
            If set to ``True`` - resulting object will be write-locked (``FOR UPDATE``)
        :type update:
            bool

        :return:
            A list of the model objects instances.
        """

        cls_pk = cls.Meta.primary_key

        if len(cls_pk) > 1:
            clause: list = []
            for pk in pks:
                if not isinstance(pk, (list, tuple)):
                    pk = [pk, ]
                if len(cls_pk) != len(pk):
                    raise RuntimeError(
                        f"Given primary key values length is different than the declared one for this model: {cls.__name__}"
                    )
                clause.append(and_(*[
                    (c == cls.Meta.casted_value(c, pk[i]))
                    for i, c in enumerate(cls_pk)
                ]))
            return await cls.all(or_(*clause), update=update)

        else:
            c = cls_pk[0]
            return await cls.all(c.in_(pks))

    @classmethod
    async def first(
            cls,
            *clause,
            offset: Optional[int] = None,
            order: Optional[Union[Any, List[Any]]] = None,
            update: bool = False,
            **filters
    ) -> 'Model':
        """ Returns a single model object by given criteria, or ``None`` if there is no object.
        The method params have been described in the :py:meth:`~select` method.
        """
        return (await cls.select(*clause, limit=1, offset=offset, order=order, update=update, **filters)).first()

    @classmethod
    async def get(cls, *pk, update: bool = False):
        """ Returns a single object identified by the given primary key value.

        :param pk:
            The primary key value criteria. If there is a complex primary key declared for the
            model - then `pk` must be a (tuple) of all primary key columns ordered the
            same as been declared in the model.

        :param update:
            If set to ``True`` - resulting object will be write-locked (``FOR UPDATE``)
        :type update:
            bool

        :return:
            a single model object or ``None`` if there is no object with given primary key.
        :rtype:
            the model object instance, or None
        """

        cls_pk = cls.Meta.primary_key
        if len(cls_pk) != len(pk):
            raise RuntimeError(
                f"Given primary key values length is different than the declared one for this model: {cls.__name__}"
            )
        return await cls.first(*[
            (c == cls.Meta.casted_value(c, pk[i]))
            for i, c in enumerate(cls_pk)
        ], update=update)

    @classmethod
    def ilike(cls, term: str) -> Optional[List[Union[BinaryExpression, UnaryExpression]]]:
        """ Returns a case-insensetive filter clause by given textual search term. The
        resulting clause may be used in the corresponding fetching methods like
        :py:meth:`~all()`, :py:meth:`~first()` and etc.
        """
        findable_attrs: Sequence[str] = cls.Meta.findable
        if not findable_attrs:
            return None
        clause: List[Union[BinaryExpression, UnaryExpression]] = []
        for name in findable_attrs:
            c: Column = getattr(cls, name)
            clause.append(cast(c, sqltypes.VARCHAR).ilike(f"%{term}%"))
        return or_(*clause)

    def json(
            self,
            attributes: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            set_name: Optional[str] = None,
            deep: Optional[Union[bool, List[str]]] = False,
    ) -> Dict[str, Any]:
        """ The shortcut method for the :py:meth:`~dict` method,
        resulting with a dict with JSONed keys ready and relative URLs.
        For explanation of the method parameters please explore the parent
        :py:meth:`~dict` method.
        """
        return self.dict(
            attributes=attributes,
            exclude=exclude,
            deep=deep,
            set_name=set_name,
            jsonify_names=True,
            fq_urls=False
        )

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
        """ Returns a case-sensetive filter clause by given textual search term. The
        resulting clause may be used in the corresponding fetching methods like
        :py:meth:`~all()`, :py:meth:`~first()` and etc.
        """
        findable_attrs: Sequence[str] = cls.Meta.findable
        if not findable_attrs:
            return None
        clause: List[Union[BinaryExpression, UnaryExpression]] = []
        for name in findable_attrs:
            c: Column = getattr(cls, name)
            clause.append(cast(c, sqltypes.VARCHAR).like(f"%{term}%"))
        return or_(*clause)

    async def update(self, **values) -> None:
        """ Updates the existing model object with passed as named arguments values.
        For example:

        .. highlight:: python
        .. code-block:: python

            await instance.update(
                name='the new name',  # udpate attribute 'name'
                sold=True,            # updaet attribute 'sold'
            )
        """
        [await self._update(k, v) for k, v in values.items()]

    @classmethod
    async def select(
            cls,
            *clause,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            order: Optional[Union[Any, List[Any]]] = None,
            update: bool = False,
            **filters
    ) -> ScalarResult:
        """ Executes the ``SELECT`` request to fetch data from the database and returns scalars results.
        Those results may be used futher to retreive the requested type of data of the request results.

        :param clause:
            A list of filtering clause (``WHERE`` clause) as SQLAlchemy expression. If more
            than one argument be given - them all will be grouped by ``AND`` expression.

            The example of the clause:

            .. highlight:: python
            .. code-block:: python

                scalars = await MyModel.select(
                    ds.or_(
                        MyModel.option.in_(['op1', 'op2']),
                        MyModel.another == 'the some value'
                    ),
                    order=MyModel.the_date.desc()
                )

        :param limit:
            Limit by given quantity of rows (transforms to the corresponding SQL "``LIMIT x``")
        :type limit:
            optional [int]

        :param offset:
            Offset from which to select rows from the corresponding table
            (transforms to the corresponding SQL "``OFFSET x``")
        :type offset:
            optional [int]

        :param order:
            Order resulting rows by given criteria. The order may be given using one of:

            *   The (str) name of the corresponding column
            *   The list of (str) names of the corresponding columns
            *   The column instance itself
            *   The list of column instances

            For descending ordering prepend the column name with minus (``'-columnn'``) if
            (str) type used, or user corresponding SQLAlchemy ``.desc()`` on the
            column instance.

        :param update:
            If set to ``True`` - then resulting rows will be locked on write preventing
            other processes from same selecting with ``update=True`` waiting for the
            current process to finish. Transforms to the SQL "``FOR UPDATE``" modifier.
        :type update: bool

        :param filters:
            For the simplier case, when filtering with ``AND`` clause only, you may use
            named arguments to indicate whose objects/rows to fetch. For example:

            .. highlight:: python
            .. code-block:: python

                # Lets get all rows where sold=True AND closed=False
                scalars = await MyModel.select(sold=True, closed=False)

        :return:
            Scalars results ready to be handled by the calling function
        :rtype:
            ``sqlalchemy.engine.result.ScalarResult``

        """
        session: AsyncSession = context['db']
        statement: Select = select(cls)
        if clause:
            statement = statement.filter(and_(*clause))
        if filters:
            statement = statement.filter_by(**cls.Meta.casted_values(**filters))

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

        if update:
            statement = statement.with_for_update()

        return (await session.execute(statement)).scalars()


DatabaseModel = declarative_base(cls=Model, metaclass=_ModelMetaclass)


@dataclass
class History:
    enable: bool = False
    model: ClassVar = None
    ignore: List[Union[str, Column]] = None
    attributes: List[Union[str, Column]] = None
    exclude: List[Union[str, Column]] = None


class Meta:
    """ The model's subclass describing some optionals and service methods for the ORM class.
    """

    model: ClassVar
    """ the class of the corresponding ORM model """

    module_name: str
    """ the name of the module where this model is declared at """

    app_name: str
    """ the name of the app where this model is declared at"""

    attributes: list
    """ the array of model attributes """

    columns: list
    """ the array of model columns """

    caption: str
    """ statically set caption of the model """

    caption_plural: str
    """ statically set caption of the model instance when speaking about
    several instances (two or more) """

    caption_key: Optional[str]
    """ the attribute name which about to be user as caption of the
    model instance, if applicable
    
    .. highlight:: python
    .. code-block:: python
    
        class MyModel(ds.Model):
            id = ds.UUIDPrimaryKey()
            name = ds.Column(ds.String(100), nullable=False, default='')
            value = ds.Column(ds.String(255))
            
            class Meta:
                caption_key = 'name'
    """

    hidden: Optional[List[str]]
    """ the array of model attributes names whose will not be included in the
    resulting dict, generated by :py:meth:`~wefram.ds.orm.model.Model.dict` 
    or :py:meth:`~wefram.ds.orm.model.Model.json` methods of the
    :py:class:`~wefram.ds.orm.model.Model` class
    
    .. highlight:: python
    .. code-block:: python
    
        class MyModel(ds.Model):
            ...
            
            class Meta:
                hidden = ['password', 'secret']
    """

    include: Optional[List[str]]
    """ the array of model attributes names whose normally not about to be
    included in the resulting dict, generated by :py:meth:`~wefram.ds.orm.model.Model.dict`
    or :py:meth:`~wefram.ds.orm.model.Model.json` of the 
    :py:class:`~wefram.ds.orm.model.Model` class, but has to be
    
    .. highlight:: python
    .. code-block:: python
    
        class MyModel(ds.Model):
            ...
            
            class Meta:
                include = ['some_property', 'some_non_column'] 
    """

    attributes_sets: Optional[Dict[str, Sequence[str]]]
    """ a dict of sets of attributes, useful when need to return only
    specific attributes of the model in the resuling dict, generated
    by :py:meth:`~wefram.ds.orm.model.Model.dict` or 
    :py:meth:`~wefram.ds.orm.model.Model.json` methods of the
    :py:class:`~wefram.ds.orm.model.Model`, formed as set name and
    corresponding list of the set attributes
    
    .. highlight:: python
    .. code-block:: python
    
        class MyModel(ds.Model):
            id = ds.UUIDPrimaryKey()
            name = ds.Column(ds.String(100), nullable=False, default='')
            public = ds.Column(ds.String(255))
            other = ds.Column(ds.String(255))
            
            class Meta:
                attributes_sets = {
                    'publics': ['id', 'name', 'public'],
                    'identity': ['id', 'name']
                }
    """

    repr_by: Optional[List[str]]
    """ the list of attribute names used to (repr) the model instance,
    which may help programmer to identify the object as the
    specific instance; for example, default repr with set ``repr_by``
    to ['id', 'name'] will result in something like:
    <MyModel id=1 name=My name>
    """

    findable: Optional[List[str]]
    """ the list of attribute names used to find by a textual term """

    order: Optional[Union[str, List[str], Column, List[Column]]]
    """ the default sorting rule, in the format used by SQLAclhemy
    with default 'sort'
    """

    history: History
    """ (history) """

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
        if v is None:
            return None
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

