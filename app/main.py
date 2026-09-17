from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import model as _models  # noqa: F401 — register ORM mappers
from app.core.database.engine import engine
from app.core.database.health import database_health_check
from app.core.database.schema_ensure import ensure_schema_patches
from app.core.database.session import AsyncSessionLocal
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import authentication_middleware, log_requests
from app.core.responses import ResponseBuilder
from app.shared.routers import api_router

setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await ensure_schema_patches(engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
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
async def health():
    """Public liveness/readiness probe (DB connectivity)."""
    db_ok = False
    reason: str | None = None
    try:
        async with AsyncSessionLocal() as session:
            db_ok, reason = await database_health_check(session)
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"[:240]

    payload = {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "reason": reason,
    }
    if db_ok:
        return ResponseBuilder.success(data=payload, message="Healthy")
    return JSONResponse(
        status_code=503,
        content=ResponseBuilder.failure(
            message="Database unavailable",
            status_code=503,
            errors=["DATABASE_DOWN", reason] if reason else ["DATABASE_DOWN"],
        ).model_dump(),
    )
