import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import UJSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(None, description="Код ошибки")
    field: Optional[str] = Field(
        None, description="Поле, в котором произошла ошибка валидации"
    )
    context: Optional[dict] = Field(None, description="Дополнительный контекст ошибки")


class ErrorResponse(BaseModel):
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: str = Field(..., description="Код ошибки")

    timestamp: datetime = Field(
        default_factory=datetime.now, description="Время возникновения ошибки"
    )
    status_code: int = Field(..., description="HTTP статус код ошибки")
    detail: List[ErrorDetail] = Field(..., description="Детали ошибки")
    context: Dict[str, Any] = Field(..., description="Дополнительный контекст ошибки")


class BaseHTTPException(HTTPException):

    def __init__(
        self,
        status_code: int,
        detail: Union[str, ErrorResponse],
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}

        self.format_detail()

    def format_detail(self) -> None:
        if isinstance(self.detail, str):
            self.detail = ErrorResponse(
                message=self.detail,
                error_code=self.error_code,
                status_code=self.status_code,
                detail=[],
                context=self.context,
            )


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


class InternalServerError(BaseHTTPException):

    def __init__(
        self,
        detail: str = "Внутренняя ошибка сервера",
        error_code: str = "internal_server_error",
        **context,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            context=context,
        )


class ServiceUnavailableError(BaseHTTPException):
    def __init__(
        self,
        detail: str = "Сервис недоступен",
        error_code: str = "service_unavailable",
        **context,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
            context=context,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseHTTPException)
    async def http_exception_handler(
        request: Request, exc: BaseHTTPException
    ) -> UJSONResponse:
        if exc.status_code != status.HTTP_404_NOT_FOUND:
            logger.warning(
                f"Ошибка {exc.status_code}: {exc.detail}",
                extra={
                    "error_code": exc.error_code,
                    "path": request.url.path,
                    "method": request.method,
                    **exc.context,
                },
            )
        content = jsonable_encoder(exc.detail)
        return UJSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> UJSONResponse:

        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        logger.info(
            f"Ошибка валидации запроса: {errors}", extra={"path": request.url.path}
        )

        return UJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "message": "Ошибка валидации запроса",
                "error_code": "validation_error",
                "validation_errors": errors,
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> UJSONResponse:
        logger.info(f"ошибка 404: {request.url.path}", extra={"method": request.method})

        return UJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": f"Страница {request.url.path} не найдена",
                "error_code": "Router_not_found",
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> UJSONResponse:

        logger.error(
            f"Необработанная ошибка: {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method},
        )

        is_production = False
        error_detail = str(exc) if not is_production else "Внутренняя ошибка сервера"

        return UJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Внутренняя ошибка сервера",
                "error_code": "internal_server_error",
                "detail": error_detail if not is_production else None,
            },
        )
