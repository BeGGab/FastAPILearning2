import uuid
import httpx
from pydantic import ValidationError

from src.config import Settings

from src.Models.Client.schema import AuthorPayload
from src.Models.exception.client_exception import NotFoundError, ValidationError as AppValidationError


class AuthorServiceClient:
    def __init__(self) -> None:
        self._settings = Settings()

    async def validate_author(self, author_id: uuid.UUID) -> uuid.UUID:
        base_url = str(self._settings.main_service_url).rstrip("/")
        timeout = self._settings.main_service_timeout_seconds
        url = f"{base_url}/api/v1/authors_books/{author_id}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            raise NotFoundError(detail=f"Автор с id {author_id} не найден в главном сервисе")

        if response.status_code >= 400:
            raise AppValidationError(
                detail="Главный сервис недоступен или вернул ошибку при проверке автора",
                service="main_service",
                status_code=response.status_code,
            )

        try:
            payload = AuthorPayload.model_validate(response.json())
        except (ValidationError, ValueError) as e:
            raise AppValidationError(
                detail="Главный сервис вернул некорректный формат автора",
                service="main_service",
            ) from e

        return payload.id

