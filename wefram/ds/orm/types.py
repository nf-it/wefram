from typing import *
import uuid
from abc import ABC
from sqlalchemy.schema import *
from sqlalchemy.types import *
from sqlalchemy.dialects.postgresql import UUID, JSONB


class Attribute:
    def __init__(self):
        self.parent_key = None
        self.parent_class = None


def _new_uuid4():
    return uuid.uuid4().hex


def _uuid_primary_key_column():
    return Column(UUID(), primary_key=True, default=_new_uuid4, unique=True)


def _serial_column(
        start: int = 1,
        increment: int = 1
):
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
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Caption(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 100)
        super().__init__(*args, **kwargs)


class StringChoice(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, choices: Union[List[str], tuple, Dict[str, Any]], **kwargs):
        optlen: int = max([len(key) for key in choices])
        kwargs.setdefault('length', optlen)
        super().__init__(**kwargs)
        self.choices_items = choices


class IntegerChoice(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, choices: Union[List[int], tuple, Dict[int, Any]], **kwargs):
        super().__init__(**kwargs)
        self.choices_items = choices


class Email(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 200)
        super().__init__(*args, **kwargs)


class Phone(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('length', 20)
        super().__init__(*args, **kwargs)
