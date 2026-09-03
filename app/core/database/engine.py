# app/core/database/engine.py

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config.settings import settings


def _connect_args() -> dict:
    host = (make_url(settings.DATABASE_URL).host or "").lower()
    args: dict = {"timeout": 30}
    if host.endswith(".railway.internal"):
        args["ssl"] = False
    elif host.endswith(".rlwy.net"):
        args["ssl"] = True
    return args


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args(),
)