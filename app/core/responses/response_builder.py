from http import HTTPStatus

from app.core.responses.api_response import ApiResponse
from app.core.responses.http_status import StatusCode


class ResponseBuilder:
    @staticmethod
    def success(
        data=None,
        message: str = "Success",
    ) -> ApiResponse:
        return ApiResponse(
            success=True,
            message=message,
            status_code=HTTPStatus.OK,
            data=data,
        )

    @staticmethod
    def created(
        data=None,
        message: str = "Created successfully",
    ) -> ApiResponse:
        return ApiResponse(
            success=True,
            message=message,
            status_code=HTTPStatus.CREATED,
            data=data,
        )

    @staticmethod
    def failure(
        message: str,
        status_code: int = HTTPStatus.BAD_REQUEST,
        errors: list[str] | None = None,
    ) -> ApiResponse:
        return ApiResponse(
            success=False,
            message=message,
            status_code=status_code,
            errors=errors,
        )

    @staticmethod
    def deleted(
        message: str = "Deleted successfully",
        errors: list[str] | None = None,
    ) -> ApiResponse:
        return ApiResponse(
            success=True,
            message=message,
            status_code=StatusCode.NO_CONTENT,
            errors=errors,
        )

    # Backward-compatible alias used by existing Identity routers
    Deleted = deleted

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized.",
        errors: list[str] | None = None,
    ) -> ApiResponse:
        return ApiResponse(
            success=False,
            message=message,
            status_code=StatusCode.UNAUTHORIZED,
            errors=errors,
        )

    Unauthorized = unauthorized

    @staticmethod
    def unprocessable_entity(
        message: str = "Unprocessable entity",
        errors: list[str] | None = None,
    ) -> ApiResponse:
        return ApiResponse(
            success=False,
            message=message,
            status_code=StatusCode.UNPROCESSABLE_ENTITY,
            errors=errors,
        )

    Unprocessably_entity = unprocessable_entity
