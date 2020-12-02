from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo_pool="debug",
    pool_use_lifo=True,
)
AsyncSessionLocal = AsyncSession(autocommit=False, autoflush=False, bind=engine)
