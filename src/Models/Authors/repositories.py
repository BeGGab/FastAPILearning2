import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Models.Authors.model import BiographyAuthor

from src.Models.Authors.schema import SBiographerCreate, SBiographerUpdate


class BiographyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def created(self, biography_data: SBiographerCreate) -> BiographyAuthor:
        biography = biography_data.to_orm_model()
        return biography

    async def get_id(self, author_id: uuid.UUID) -> Optional[BiographyAuthor]:
        query = select(BiographyAuthor).filter_by(author_id=author_id)
        result = await self.session.execute(query)
        return result.unique().scalar()

    async def update(
        self, biography_id: uuid.UUID, biographt_data: SBiographerUpdate
    ) -> BiographyAuthor:
        biography = await self.get_id(author_id=biography_id)
        biographt_data.apply_updates(biography)
        return biography
