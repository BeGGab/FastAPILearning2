import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from src.models.authors.schema import (
    SBiographerCreate,
    SBiographerRead,
    SBiographerUpdate,
)
from src.dependencis import get_biography_service
from src.models.authors.service import BiographyService

router = APIRouter(prefix="/api/v1/biographies", tags=["biographies"])




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_biography(
    payload: SBiographerCreate,
    service: BiographyService = Depends(get_biography_service),
) -> SBiographerRead:
    return await service.create_biography(biography_data=payload)


@router.get("/{author_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_biography(
    author_id: uuid.UUID,
    service: BiographyService = Depends(get_biography_service),
) -> SBiographerRead:
    return await service.find_one_or_none_by_author_id(author_id=author_id)


