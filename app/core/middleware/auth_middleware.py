"""API authentication middleware — defense-in-depth before route handlers."""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.responses import ResponseBuilder
from app.core.security.jwt import decode_access_token

logger = logging.getLogger(__name__)

PUBLIC_API_PATHS: frozenset[str] = frozenset(
    {
        "/api/v1/auth/login",
    }
)

PUBLIC_PATH_PREFIXES: tuple[str, ...] = (
    "/docs",
    "/redoc",
    "/openapi.json",
)


def _unauthorized(message: str = "Authentication token is required.") -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ResponseBuilder.failure(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=["UNAUTHORIZED"],
        ).model_dump(),
    )


async def authentication_middleware(request: Request, call_next):
    path = request.url.path

    if request.method == "OPTIONS":
        return await call_next(request)

    if path in {"/", "/health"} or any(
        path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES
    ):
        return await call_next(request)

    if path in PUBLIC_API_PATHS:
        return await call_next(request)

    if not path.startswith("/api/v1"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return _unauthorized()

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return _unauthorized()

    try:
        payload = decode_access_token(token)
    except Exception:
        logger.debug("Invalid token on %s %s", request.method, path)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ResponseBuilder.failure(
                message="Authentication token is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                errors=["INVALID_TOKEN"],
            ).model_dump(),
        )

    request.state.user_id = payload.get("sub")
    request.state.token_payload = payload

    return await call_next(request)
