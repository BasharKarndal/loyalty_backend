# app/core/database/engine.py

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,

    echo=settings.DEBUG,

    future=True,

    pool_pre_ping=True,
)