from typing import *
from sqlalchemy.sql import Select, Executable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult, Row, Result
from sqlalchemy.util import EMPTY_DICT
from ...requests import context


__all__ = [
    'all',
    'one',
    'first',
    'one_or_none',
    'scalar_one',
    'scalar_one_or_none',
    'scalars',
    'scalar',
]


def _get_context_connection() -> AsyncSession:
    return context['db']


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
) -> Result:
    session: AsyncSession = _get_context_connection()
    return await session.execute(
        statement=statement,
        params=params,
        execution_options=execution_options,
        bind_arguments=bind_arguments,
        **kw
    )


async def all(statement: Select, **kwargs) -> List[Row]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().all()


async def one(statement: Select, **kwargs) -> Row:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one()


async def first(statement: Select, **kwargs) -> Row:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().first()


async def one_or_none(statement: Select, **kwargs) -> Optional[Row]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars().one_or_none()


async def scalar_one(statement: Select, **kwargs) -> Any:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one()


async def scalar_one_or_none(statement: Select, **kwargs) -> Optional[Any]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar_one_or_none()


async def scalar(statement: Select, **kwargs) -> Optional[Any]:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalar()


async def scalars(statement: Select, index: int, **kwargs) -> ScalarResult:
    session: AsyncSession = _get_context_connection()
    return (await session.execute(statement)).scalars()
