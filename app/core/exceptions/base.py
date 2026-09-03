from fastapi import status

class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: list | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []

        super().__init__(message)