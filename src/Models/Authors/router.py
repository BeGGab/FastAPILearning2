import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from src.models.authors.schema import (
    SBiographerCreate,
    SBiographerRead,
    SBiographerUpdate,
)
from src.models.core.dependencis import get_biography_service
from src.models.authors.service import BiographyService

router = APIRouter(prefix="/api/v1/biographies", tags=["biographies"])




@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_biography(
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


@router.put("/{biography_id}", status_code=status.HTTP_201_CREATED)
async def updated_biography(
    biography_id: uuid.UUID,
    payload: SBiographerUpdate,
    service: BiographyService = Depends(get_biography_service),
) -> SBiographerRead:
    return await service.update_biography(
        biography_id=biography_id, biography_data=payload
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deleted_biography(
    id: uuid.UUID,
    service: BiographyService = Depends(get_biography_service),
):
    await service.delete_biography(biography_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
