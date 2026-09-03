from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import model as _models  # noqa: F401 — register ORM mappers
from app.core.database.health import database_health_check
from app.core.database.session import get_session
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import authentication_middleware, log_requests
from app.core.responses import ResponseBuilder
from app.shared.routers import api_router

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Clean Architecture + Modular bounded contexts. "
        "Stack: FastAPI, SQLAlchemy 2 Async, PostgreSQL, Alembic, Pydantic v2, JWT."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.middleware("http")(authentication_middleware)
app.middleware("http")(log_requests)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    """Public liveness/readiness probe (DB connectivity)."""
    db_ok = await database_health_check(session)
    payload = {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
    if db_ok:
        return ResponseBuilder.success(data=payload, message="Healthy")
    return JSONResponse(
        status_code=503,
        content=ResponseBuilder.failure(
            message="Database unavailable",
            status_code=503,
            errors=["DATABASE_DOWN"],
        ).model_dump(),
    )
