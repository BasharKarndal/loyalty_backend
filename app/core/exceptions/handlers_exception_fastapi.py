from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.responses import ResponseBuilder


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = []

        for error in exc.errors():
            field = error["loc"][-1]

            if error["type"] == "missing":
                message = f"{field.capitalize()} is required."
            elif error["type"] == "string_too_short":
                message = f"{field.capitalize()} is required."
            else:
                message = error["msg"]

            errors.append(
                {
                    "field": field,
                    "message": message,
                }
            )

        first = errors[0]["field"]

        return JSONResponse(
            status_code=422,
            content=ResponseBuilder.error(
                message="Unprocessable Content",
                status_code=422,
                errors=errors,
            ),
)