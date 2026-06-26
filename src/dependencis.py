from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.authors.service import BiographyService
from src.models.authors.repositories import BiographyRepository
from src.db import get_async_session


async def get_biography_service(
    session: AsyncSession = Depends(get_async_session),
) -> BiographyService:
    return BiographyService(session, BiographyRepository(session))