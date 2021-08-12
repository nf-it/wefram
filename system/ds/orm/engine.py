from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
import config


__all__ = [
    'engine',
    'Session',
]


engine: AsyncEngine = create_async_engine(
    'postgresql+asyncpg://{user}:{pass}@{host}:{port}/{name}'.format(**config.DATABASE),
    echo=bool(getattr(config, 'ECHO_DS', False))
)
Session: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession)
