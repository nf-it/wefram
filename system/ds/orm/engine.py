from asyncio import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session
import config


__all__ = [
    'engine',
    'AsyncSession',
]


engine: AsyncEngine = create_async_engine(
    'postgresql+asyncpg://{user}:{pass}@{host}:{port}/{name}'.format(**config.DATABASE),
    # pool_size=1,
    echo=bool(getattr(config, 'ECHO_DS', False))
)
Session: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, autoflush=True, expire_on_commit=False)
AsyncSession = async_scoped_session(Session, scopefunc=current_task)
