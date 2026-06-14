import uuid
import logging
import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.authors.schema import (
    SBiographerCreate,
    SBiographerRead,
    SBiographerUpdate,
)

from src.models.authors.repositories import BiographyRepository

from src.models.core.exception import NotFoundError, ValidationError


logger = logging.getLogger(__name__)


class BiographyService:
    def __init__(self, session: AsyncSession, repository: BiographyRepository):
        self.session = session
        self.repository = repository


    async def create_biography(
        self, biography_data: SBiographerCreate
    ) -> SBiographerRead:
        enriched_biography_data = biography_data.model_copy(
            update={"author_id": biography_data.author_id}
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


