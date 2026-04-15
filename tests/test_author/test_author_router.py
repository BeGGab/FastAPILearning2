import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_router_create_get_update_delete(async_client: AsyncClient):
    author_id = uuid.uuid4()

    create_resp = await async_client.post(
        "/api/v1/biographies/",
        json={
            "author_id": str(author_id),
            "text": "router bio",
            "year_of_birth": 1888,
            "year_of_death": 1955,
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    biography_id = created["id"]
    assert created["author_id"] == str(author_id)

    get_resp = await async_client.get(f"/api/v1/biographies/{author_id}")
    assert get_resp.status_code == 206
    assert get_resp.json()["text"] == "router bio"

    put_resp = await async_client.put(
        f"/api/v1/biographies/{biography_id}",
        json={"text": "updated"},
    )
    assert put_resp.status_code == 201
    assert put_resp.json()["text"] == "updated"

    del_resp = await async_client.delete(f"/api/v1/biographies/{biography_id}")
    assert del_resp.status_code == 204

    missing = await async_client.get(f"/api/v1/biographies/{author_id}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_router_get_unknown_author_returns_404(async_client: AsyncClient):
    resp = await async_client.get(f"/api/v1/biographies/{uuid.uuid4()}")
    assert resp.status_code == 404
