from asyncio import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session
from ... import config


__all__ = [
    'engine',
    'AsyncSession',
]


engine: AsyncEngine = create_async_engine(
    'postgresql+asyncpg://{user}:{pass}@{host}:{port}/{name}'.format(**config.DATABASE),
    # pool_size=1,
    echo=bool(getattr(config, 'ECHO_DS', False)),
    # query_cache_size=0,
    pool_pre_ping=True
)
_AsyncSession: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, autoflush=True, expire_on_commit=False)
AsyncSession = async_scoped_session(_AsyncSession, scopefunc=current_task)
