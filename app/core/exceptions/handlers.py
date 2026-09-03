from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.responses import ResponseBuilder
from .base import AppException


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseBuilder.failure(
                message=exc.message,
                status_code=exc.status_code,
                errors=exc.errors,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = []

        for error in exc.errors():
            errors.append(
                {
                    "field": error["loc"][-1],
                    "message": error["msg"],
                }
            )

        return JSONResponse(
            status_code=422,
            content=ResponseBuilder.failure(
                message="Validation failed.",
                status_code=422,
                errors=errors,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(
        request: Request,
        exc: Exception,
    ):
        return JSONResponse(
            status_code=500,
            content=ResponseBuilder.failure(
                message="Internal server error.",
                status_code=500,
                errors=["INTERNAL_SERVER_ERROR"],
            ).model_dump(),
        )