import uuid

import pytest

from src.models.authors.repositories import BiographyRepository
from src.models.authors.schema import SBiographerCreate, SBiographerUpdate  
from src.models.authors.service import BiographyService

from src.exception import NotFoundError


@pytest.mark.asyncio
async def test_create_biography_persists_and_reads_by_author(biography_session):
    author_id = uuid.uuid4()
    service = BiographyService(biography_session, BiographyRepository(biography_session))

    created = await service.create_biography(
        SBiographerCreate(
            author_id=author_id,
            text="Текст биографии",
            year_of_birth=1900,
            year_of_death=1955,
        )
    )
    await biography_session.commit()

    assert created.author_id == author_id
    assert created.text == "Текст биографии"

    read = await service.find_one_or_none_by_author_id(author_id)
    assert read.id == created.id
    assert read.year_of_birth == 1900


@pytest.mark.asyncio
async def test_find_by_author_not_found_raises(biography_session):
    service = BiographyService(biography_session, BiographyRepository(biography_session))

    with pytest.raises(NotFoundError):
        await service.find_one_or_none_by_author_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_biography(biography_session):
    author_id = uuid.uuid4()
    service = BiographyService(biography_session, BiographyRepository(biography_session))

    created = await service.create_biography(
        SBiographerCreate(
            author_id=author_id,
            text="old",
            year_of_birth=1910,
            year_of_death=2000,
        )
    )
    await biography_session.commit()

    updated = await service.update_biography(
        created.id,
        SBiographerUpdate(text="new", year_of_death=2001),
    )
    await biography_session.commit()

    assert updated.text == "new"
    assert updated.year_of_death == 2001
    assert updated.year_of_birth == 1910


@pytest.mark.asyncio
async def test_delete_biography(biography_session):
    author_id = uuid.uuid4()
    service = BiographyService(biography_session, BiographyRepository(biography_session))

    created = await service.create_biography(
        SBiographerCreate(
            author_id=author_id,
            text="x",
            year_of_birth=1,
            year_of_death=2,
        )
    )
    await biography_session.commit()

    await service.delete_biography(created.id)
    await biography_session.commit()

    with pytest.raises(NotFoundError):
        await service.find_one_or_none_by_author_id(author_id)
