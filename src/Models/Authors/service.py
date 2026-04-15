import uuid
import logging
import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client.author_client import AuthorServiceClient
from src.models.authors.schema import (
    SBiographerCreate,
    SBiographerRead,
    SBiographerUpdate,
)

from src.models.authors.repositories import BiographyRepository

from src.models.exception.client_exception import ValidationError, NotFoundError


logger = logging.getLogger(__name__)


class BiographyService:
    def __init__(self, session: AsyncSession, repository: BiographyRepository):
        self.session = session
        self.author_service_client = AuthorServiceClient()
        self.repository = repository


    async def create_biography(
        self, biography_data: SBiographerCreate
    ) -> SBiographerRead:
        try:
            verified_author_id = await self.author_service_client.validate_author(
                biography_data.author_id
            )
        except httpx.RequestError as exc:
            logger.error("Ошибка сети при обращении к сервису авторов", exc_info=True)
            raise ValidationError(
                detail="Не удалось проверить автора в сервисе авторов"
            ) from exc

        enriched_biography_data = biography_data.model_copy(
            update={"author_id": verified_author_id}
        )
        biography = await self.repository.created(enriched_biography_data)
        if not biography:
            logger.error(f"Ошибка при создании биографии")
            raise ValidationError(detail="Ошибка при создании биографии")

        self.session.add(biography)
        await self.session.flush()
        await self.session.refresh(biography)
        return SBiographerRead.model_validate(biography, from_attributes=True)

    async def find_one_or_none_by_author_id(self, author_id: uuid.UUID) -> SBiographerRead:
        biography = await self.repository.get_by_author_id(author_id=author_id)
        if not biography:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Биография с id {author_id} не найдена")
        return SBiographerRead.model_validate(biography, from_attributes=True)

    async def update_biography(
        self, biography_id: uuid.UUID, biography_data: SBiographerUpdate
    ) -> SBiographerRead:
        biography = await self.repository.update(
            biography_id, biography_data
        )
        if not biography:
            logger.error(f"Ошибка при поиске записи в базе данных")
            raise NotFoundError(detail=f"Биография с id {biography_id} не найдена")

        await self.session.flush()
        await self.session.refresh(biography)
        return SBiographerRead.model_validate(biography, from_attributes=True)

    async def delete_biography(self, biography_id: uuid.UUID):
        biography = await self.repository.get_by_id(biography_id)
        if not biography:
            logger.error(f"Ошибка при удалении записи из базы данных")
            raise NotFoundError(detail=f"Биография с id {biography_id} не найдена")
        await self.session.delete(biography)
