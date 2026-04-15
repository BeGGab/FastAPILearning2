import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.Models.Authors.schema import (
    SBiographerCreate,
    SBiographerRead,
    SBiographerUpdate,
)
from src.Models.Authors.service import BiographyService

from src.db import get_async_session


router = APIRouter(prefix="/api/v1/biographies", tags=["biographies"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_biography(
    payload: SBiographerCreate, session: AsyncSession = Depends(get_async_session)
) -> SBiographerRead:
    return await BiographyService(session=session).create_biography(
        biography_data=payload
    )


@router.get("/{author_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_biography(
    author_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SBiographerRead:
    return await BiographyService(session).find_one_or_none_by_author_id(author_id=author_id)


@router.put("/{biography_id}", status_code=status.HTTP_201_CREATED)
async def updated_biography(
    biography_id: uuid.UUID,
    payload: SBiographerUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SBiographerRead:
    return await BiographyService(session).update_biography(
        biography_id=biography_id, biography_data=payload
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deleted_biography(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    await BiographyService(session).delete_biography(biography_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
