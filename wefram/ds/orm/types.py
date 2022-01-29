"""
Provides extra column and value types, extending default SQLAlchemy
defined ones.
"""

from typing import *
import uuid
from sqlalchemy.schema import *
from sqlalchemy.types import *
from sqlalchemy.dialects.postgresql import UUID, JSONB


def _new_uuid4():
    """ Generates the new UUID4-based primary key value. """

    return uuid.uuid4().hex


def _uuid_primary_key_column():
    """ Returns the UUID-based primary key ``Column``. """

    return Column(UUID(), primary_key=True, default=_new_uuid4, unique=True)


def _serial_column(start: int = 1, increment: int = 1):
    """ Returns the auto-increment based primary key ``Column``.
    The optional arguments provides capability to override the default
    start index and increment step.

    The ``SERIAL`` PostgreSQL type is used.

    :param start:
        The default (start) index. By default, PostgreSQL begin auto-
        increment from 1st, but this behaviuor mey be overriden with
        this parameter.

    :param increment:
        The increment step. By default, each new value increment by '1',
        but this behaviuor may be overriden with this parameter.

    :return:
        The Column definition for the auto-increment column type.
    :rtype:
        ``Column``
    """

    return Column(
        Integer(),
        Identity(start=start, increment=increment, cycle=True),
        primary_key=True,
        nullable=False,
        unique=True
    )


def _bigserial_column(
        start: int = 1,
        increment: int = 1
):
    """ Returns the auto-increment based primary key ``Column``.
    The optional arguments provides capability to override the default
    start index and increment step.

    The ``BIGSERIAL`` PostgreSQL type is used.

    :param start:
        The default (start) index. By default, PostgreSQL begin auto-
        increment from 1st, but this behaviuor mey be overriden with
        this parameter.

    :param increment:
        The increment step. By default, each new value increment by '1',
        but this behaviuor may be overriden with this parameter.

    :return:
        The Column definition for the auto-increment column type.
    :rtype:
        ``Column``
    """

    return Column(
        BigInteger(),
        Identity(start=start, increment=increment, cycle=True),
        primary_key=True,
        nullable=False,
        unique=True
    )


UUIDPrimaryKey = _uuid_primary_key_column
Serial = _serial_column
BigSerial = _bigserial_column
AutoIncrement = _serial_column
BigAutoIncrement = _bigserial_column


class Password(TypeDecorator):
    """
    The password implementation. Based on the ``String`` type (the
    ``VARCHAR`` on the PostgreSQL side). Will be extended with
    extra functionality later.
    """

    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return None if value is None else str(value)


class Caption(TypeDecorator):
    """
    The caption implementation, based on the ``String`` type. By
    using this column type instead of the default ``String`` one,
    the model's :prop:`~wefram.ds.Model.Meta.caption` will be
    assigned to this declaring attribute.
    """

    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 100)
        super().__init__(*args, **kwargs)

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return str(value) if value else ""


class StringChoice(TypeDecorator):
    """
    Extends the ``String`` column type with choice restriction. Automatically
    selects the length of the corresponding column type basing on the given
    choice of values.

    By implementing this type instead of default ``String`` one, there become
    a posibility for direct automation of the frontend field selection basing
    on the given options declaration.

    Raises ``KeyError`` exception if the assigning value is out of given
    given options list.

    :param choices:
        If set to ``list`` or ``tuple`` type - the each element of the given
        list|tuple represents the each option value;
        otherwise if set to ``dict`` - each item's key will be represented
        as value (stored in the databases' row's cell), the the corresponding
        dict's value will be represented as item's caption.
    """

    impl = String
    cache_ok = True

    def __init__(self, choices: Union[List[str], tuple, Dict[str, Any]], **kwargs):
        optlen: int = max([len(key) for key in choices])
        kwargs.setdefault('length', optlen)
        super().__init__(**kwargs)
        self.choices_items = choices
        self._options: List[str]

        if isinstance(choices, (list, tuple)):
            self._options = choices

        elif isinstance(choices, dict):
            self._options = list(choices.keys())

        else:
            raise ValueError("StringChoice(choices=) must be list or dict type.")

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        if value not in self.choices_items:
            raise KeyError(
                f"key '{value}' is not in the declared StringChoice(choices=)"
            )
        return value

    def process_result_value(self, value, dialect):
        return str(value) if value else None


class IntegerChoice(TypeDecorator):
    """
    Extends the ``Integer`` column type with choice restriction.

    By implementing this type instead of default ``Integer`` one, there become
    a posibility for direct automation of the frontend field selection basing
    on the given options declaration.

    Raises ``ValueError`` exception if the assigning value is out of given
    given options list.

    :param choices:
        If set to ``list`` or ``tuple`` type - the each element of the given
        list|tuple represents the each option value;
        otherwise if set to ``dict`` - each item's key will be represented
        as value (stored in the databases' row's cell), the the corresponding
        dict's value will be represented as item's caption.
    """

    impl = Integer
    cache_ok = True

    def __init__(self, choices: Union[List[int], tuple, Dict[int, Any]], **kwargs):
        super().__init__(**kwargs)
        self.choices_items = choices
        self._options: List[int]

        if isinstance(choices, (list, tuple)):
            self._options = choices

        elif isinstance(choices, dict):
            self._options = list(choices.keys())

        else:
            raise ValueError("IntegerChoice(choices=) must be list or dict type.")

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return int

    def process_bind_param(self, value, dialect):
        if value not in self.choices_items:
            raise KeyError(
                f"key '{value}' is not in the declared IntegerChoice(choices=)"
            )
        return value

    def process_result_value(self, value, dialect):
        return int(value) if value else None


class Email(TypeDecorator):
    """
    The special case of the ``String`` column type, representing the email address.
    This type made, mainly, for the future functionality extension. For this moment
    this is just a ``String`` redeclartion with default length value.

    Recommended to use this type for email addresses already, to not to refactor
    in future.
    """

    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 200)
        super().__init__(*args, **kwargs)

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return str(value) if value is not None else None


class Phone(TypeDecorator):
    """
    The special case of the ``String`` column type, representing the phone number.
    This type made, mainly, for the future functionality extension. For this moment
    this is just a ``String`` redeclartion with default length value.

    Recommended to use this type for phone numbers already, to not to refactor
    in future.
    """

    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 20)
        super().__init__(*args, **kwargs)

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return str(value) if value is not None else None
