from typing import *
from sqlalchemy import Column, Table, not_
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.sqltypes import TypeEngine
import inspect
from .model import *


__all__ = [
    'clause_eq_for_c',
    'ModelName',
    'ModelColumn',
    'TableNameOf',
    'TableColumn',
    'TableColumnOf',
    'TableOf'
]


def clause_eq_for_c(c: QueryableAttribute, value: Any, allow_text_aliases: bool = True) -> ClauseElement:

    def _conform_type(_val: Any, _type: Any) -> Any:
        return _type(_val)

    comparator: ColumnProperty.Comparator = c.comparator
    comparator_type: TypeEngine = comparator.type
    python_type: Any = comparator_type.python_type
    invert: bool = False

    if allow_text_aliases and isinstance(value, str) and value.startswith('~'):
        value = value[1:]
        if not value.startswith('~'):
            invert = True

    if allow_text_aliases and isinstance(value, str):
        alias = value.upper()
        if alias == '__NULL__':
            return c.is_(None)
        elif alias == '__NOTNULL__':
            return not_(c.is_(None))
        elif alias == '__TRUE__':
            value = True
        elif alias == '__FALSE__':
            value = False

    clause: ClauseElement

    if value is None:
        clause = c.is_(None)

    elif isinstance(value, (list, set)):
        array = [_conform_type(e, python_type) for e in value]
        clause = c.in_(array) if not invert else c.not_in(array)

    elif isinstance(value, bool) and python_type is bool:
        clause = c.is_(value)

    elif isinstance(value, bool):
        if python_type in (int, float, complex):
            clause = c != 0 if value is True else c == 0
        elif python_type is str:
            clause = c != '' if value is True else c == ''
        else:
            clause = c.is_(value)

    elif isinstance(value, str) and python_type is bool:
        state: bool = (value.lower() not in ('false', '0', 'no', 'disable', 'disabled'))
        clause = c.is_(state)

    elif isinstance(value, str) and value.startswith('%(') and value.endswith(')%'):
        value = f"%{value[2:-2]}%"
        clause = c.ilike(value) if not invert else c.not_ilike(value)

    elif isinstance(value, str) and value.startswith('%^') and value.endswith(')%'):
        value = f"{value[2:-2]}%"
        clause = c.ilike(value) if not invert else c.not_ilike(value)

    elif isinstance(value, str) and value.startswith('%(') and value.endswith('$%'):
        value = f"%{value[2:-2]}"
        clause = c.ilike(value) if not invert else c.not_ilike(value)

    elif isinstance(value, str) and value.startswith('%^') and value.endswith('$%'):
        value = f"{value[2:-2]}"
        clause = c.ilike(value) if not invert else c.not_ilike(value)

    else:
        clause = c == _conform_type(value, python_type)

    return clause if not invert else not_(clause)


class ModelName:
    def __init__(self, name: str, app: Optional[str] = None):
        self.name: str = name
        self.app: Optional[str] = app

    def __call__(self) -> ClassVar['Model']:
        return get_model(self.name, self.app)


class ModelColumn:
    def __init__(self, model_name: str, column_name: str):
        self.model_name: str = model_name
        self.column_name: str = column_name

    def __call__(self) -> [ClassVar[Column], None]:
        model: [ClassVar['Model'], None] = get_model(self.model_name)
        if model is None:
            return None
        return getattr(model, self.column_name, None)


class TableNameOf:
    def __init__(self, model: [str, ClassVar['Model']]):
        self.model: [str, ClassVar['Model']] = model

    def __call__(self) -> str:
        return str(tablename_of(self.model))


class TableColumn:
    def __init__(self, table_name: str, column_name: str):
        self.table_name: str = table_name
        self.column_name: str = column_name

    def __call__(self) -> str:
        return '.'.join([self.table_name, self.column_name])


class TableColumnOf:
    def __init__(self, model: [str, ClassVar['Model']], column_name: str):
        self.model: [str, ClassVar['Model']] = model
        self.column_name: str = column_name

    def __call__(self) -> [None, str]:
        tablename: str = tablename_of(self.model)
        if tablename is None:
            return None
        return '.'.join([tablename, self.column_name])


class TableOf:
    def __init__(self, model: [str, ClassVar['Model']]):
        self.model: [str, ClassVar['Model']] = model

    def __call__(self) -> [Table, None]:
        if inspect.isclass(self.model) and issubclass(self.model, Model):
            return self.model.__table__
        model: ClassVar['Model'] = get_model(self.model)
        if model is None:
            return None
        return model.__table__

