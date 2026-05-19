from src.models.core.base import BaseHTTPException
from fastapi import status


class BadRequestError(BaseHTTPException):

    def __init__(
        self,
        detail: str = "Неверный запрос",
        error_code: str = "bad_request",
        **context,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            context=context,
        )


class NotFoundError(BaseHTTPException):

    def __init__(
        self, detail: str = "Ресурс не найден", error_code: str = "not_found", **context
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            context=context,
        )


class ConflictError(BaseHTTPException):

    def __init__(
        self,
        detail: str = "Ресурс уже существует",
        error_code: str = "conflict",
        **context,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
            context=context,
        )


class ValidationError(BadRequestError):
    def __init__(
        self,
        detail: str = "Ошибка валидации",
        error_code: str = "validation_error",
        **context,
    ):
        super().__init__(detail=detail, error_code=error_code, **context)
        self.status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
