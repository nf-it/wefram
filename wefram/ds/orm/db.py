from typing import *
from sqlalchemy import delete, and_
from sqlalchemy.sql import Select, Executable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult, Row, Result, ChunkedIteratorResult
from sqlalchemy.util import EMPTY_DICT
from ...runtime import context


__all__ = [
    'all',
    'connection',
    'execute',
    'flush',
    'commit',
    'rollback',
    'all',
    'one',
    'delete_where',
    'fetch_all',
    'fetch_first',
    'fetch_one_or_none',
    'first',
    'one',
    'one_or_none',
    'scalar_one',
    'scalar_one_or_none',
    'scalars',
    'scalar',
]


def _get_context_connection() -> AsyncSession:
    return context['db']


def connection() -> AsyncSession:
    return _get_context_connection()


async def flush() -> None:
    session: AsyncSession = _get_context_connection()
    await session.flush()


async def commit() -> None:
    session: AsyncSession = _get_context_connection()
    await session.commit()


async def rollback() -> None:
    session: AsyncSession = _get_context_connection()
    await session.rollback()


async def execute(
        statement: Executable,
        params: Optional[Mapping] = None,
        execution_options: Mapping = EMPTY_DICT,
        bind_arguments: Optional[Mapping] = None,
        **kw
) -> Union[Result, ChunkedIteratorResult]:
    session: AsyncSession = _get_context_connection()
    return await session.execute(
        statement=statement,
        params=params,
        execution_options=execution_options,
        bind_arguments=bind_arguments,
        **kw
    )


async def all(statement: Select) -> List[Row]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().all()


async def one(statement: Select) -> Row:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one()


async def first(statement: Select) -> Row:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().first()


async def one_or_none(statement: Select) -> Optional[Row]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one_or_none()


async def scalar_one(statement: Select) -> Any:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one()


async def scalar_one_or_none(statement: Select) -> Optional[Any]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one_or_none()


async def scalar(statement: Select) -> Optional[Any]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar()


async def scalars(statement: Select) -> ScalarResult:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars()


def add(*instances):
    session: AsyncSession = _get_context_connection()
    [session.add(i) for i in instances]


async def fetch_first(statement: Executable, *args, **kwargs) -> Any:
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().first()


async def fetch_one_or_none(statement: Executable, *args, **kwargs) -> (None, Any):
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().one_or_none()


async def fetch_all(statement: Executable, *args, **kwargs) -> list:
    db = context['db']
    return (await db.execute(statement, *args, **kwargs)).scalars().all()


async def delete_where(model: ClassVar, *filter_args, **filter_kwargs) -> None:
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
