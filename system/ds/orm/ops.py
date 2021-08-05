import typing
from sqlalchemy import delete, and_
from sqlalchemy.sql.base import Executable
from sqlalchemy.engine.result import ChunkedIteratorResult
from ...requests import context
from .model import Model


__all__ = [
    'fetch_first',
    'fetch_all',
    'fetch_one_or_none',
    'execute',
    'delete_where'
]


async def fetch_first(statement: Executable, *args, **kwargs) -> typing.Any:
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().first()


async def fetch_one_or_none(statement: Executable, *args, **kwargs) -> (None, typing.Any):
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().one_or_none()


async def fetch_all(statement: Executable, *args, **kwargs) -> list:
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().all()


async def execute(statement: Executable, *args, **kwargs) -> ChunkedIteratorResult:
    db = context['db']
    return await db.execute(statement, *args, **kwargs)


async def delete_where(model: typing.ClassVar[Model], *filter_args, **filter_kwargs) -> None:
    db = context['db']
    statement = delete(model.__table__)
    where = list(filter_args)
    if filter_kwargs:
        for k in filter_kwargs:
            c = getattr(model, k, None)
            if c is None:
                raise LookupError
            where.append(c == filter_kwargs[k])
    if len(where) > 1:
        where = and_(*where)
    if where:
        statement = statement.where(where)
    return await db.execute(statement)
