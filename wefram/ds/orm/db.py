"""
Provides PostgreSQL database related common functions. The main point
on using those functions is to avoid of thinking on how and where to
get corresponding database connection.

Those functions takes the actual connection from the context. If there
is a ASGI process in use - then the request-level context connection
will be taken. If the CLI is in progress - then the local connection
will be used.
"""

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
    """ Returns the connection to the PostgreSQL database. """
    return _get_context_connection()


async def flush() -> None:
    """ Flushes changes of ORM object to the database. """
    session: AsyncSession = _get_context_connection()
    await session.flush()


async def commit() -> None:
    """ Commits the database transation. """
    session: AsyncSession = _get_context_connection()
    await session.commit()


async def rollback() -> None:
    """ Rolls back the database transaction. """
    session: AsyncSession = _get_context_connection()
    await session.rollback()


async def execute(
        statement: Executable,
        params: Optional[Mapping] = None,
        execution_options: Mapping = EMPTY_DICT,
        bind_arguments: Optional[Mapping] = None,
        **kw
) -> Union[Result, ChunkedIteratorResult]:
    """ Executes the given statement in the context of the PostgreSQL
    database connection. For parameters explanaion it is best to
    read SQLAlchemy documentation on ``execute`` function.
    """
    session: AsyncSession = _get_context_connection()
    return await session.execute(
        statement=statement,
        params=params,
        execution_options=execution_options,
        bind_arguments=bind_arguments,
        **kw
    )


async def all(statement: Select) -> List[Row]:
    """ Executes the ``SELECT`` statement and then fetch all resulting
    rows, returning them all to the calling function.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().all()


async def one(statement: Select) -> Row:
    """ Executes the ``SELECT`` statement and then return exactly one
    result or raise an exception.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one()


async def first(statement: Select) -> Row:
    """ Executes the ``SELECT`` statement and then fetch the only
    first row.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().first()


async def one_or_none(statement: Select) -> Optional[Row]:
    """ Executes the ``SELECT`` statement and then return one or zero
    results, or raise an exception for multiple rows.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one_or_none()


async def scalar_one(statement: Select) -> Any:
    """ Executes the ``SELECT`` statement and then return exactly one
    scalar result or raise an exception.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one()


async def scalar_one_or_none(statement: Select) -> Optional[Any]:
    """ Executes the ``SELECT`` statement and then return exactly
    one or no scalar result.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one_or_none()


async def scalar(statement: Select) -> Optional[Any]:
    """ Executes the ``SELECT`` statement and then return the first
    element of the first result or ``None`` if no rows present.
    If multiple rows are returned, raises ``MultipleResultsFound``.
    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar()


async def scalars(statement: Select, index: Any = 0) -> ScalarResult:
    """ Executes the ``SELECT`` statement and then return an
    :class:`AsyncScalarResult` filtering object which will return
    single elements rather than :class:`Row` objects.

    Refer to :meth:`sqlalchemy._result.Result.scalars` in the synchronous
    SQLAlchemy API for a complete behavioral description.

    :param statement:
        The statement to execute to.

    :param index:
        Integer or row key indicating the column to be fetched
        from each row, defaults to ``0`` indicating the first column.

    :return:
        A new :class:`_asyncio.AsyncScalarResult` filtering object
        referring to this :class:`_asyncio.AsyncResult` object.

    """
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars(index=index)


def add(*instances):
    """ Adds the given instances (objects of model class) to the
    current database ORM session.
    """
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
