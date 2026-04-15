import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.authors.model import BiographyAuthor

from src.models.authors.schema import SBiographerCreate, SBiographerUpdate


class BiographyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def created(self, biography_data: SBiographerCreate) -> BiographyAuthor:
        biography = biography_data.to_orm_model()
        return biography

    async def get_by_author_id(self, author_id: uuid.UUID) -> Optional[BiographyAuthor]:
        query = select(BiographyAuthor).filter_by(author_id=author_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, biography_id: uuid.UUID) -> Optional[BiographyAuthor]:
        query = select(BiographyAuthor).where(BiographyAuthor.id == biography_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, biography_id: uuid.UUID, biography_data: SBiographerUpdate
    ) -> Optional[BiographyAuthor]:
        biography = await self.get_by_id(biography_id)
        if biography is None:
            return None
        biography_data.apply_updates(biography)
        return biography
