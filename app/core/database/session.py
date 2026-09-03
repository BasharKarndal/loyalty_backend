# app/core/database/session.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.core.database.engine import engine


AsyncSessionLocal = async_sessionmaker(
    bind=engine,

    class_=AsyncSession,

    expire_on_commit=False,

    autoflush=False,
)


async def get_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    async with AsyncSessionLocal() as session:
        yield session