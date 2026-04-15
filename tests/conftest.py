from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

import pytest
from docker.errors import DockerException
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
import src.models.core.config as core_config
import src.models.core.db as db_mod 

import src.models.authors.model

from src.application import get_app
from src.models.client.author_client import AuthorServiceClient
from src.models.core.db import Base, async_session_maker, engine
_POSTGRES: PostgresContainer | None = None
_DATABASE_READY = False


def _dsn_asyncpg(url: str) -> str:
    """Testcontainers часто отдаёт postgresql+psycopg2:// — для async SQLAlchemy нужен +asyncpg."""
    parsed = urlparse(url)
    if parsed.scheme == "postgresql+asyncpg":
        return url
    if parsed.scheme in ("postgresql", "postgres") or parsed.scheme.startswith("postgresql+"):
        path = parsed.path or "/"
        return urlunparse(("postgresql+asyncpg", parsed.netloc, path, "", "", ""))
    return url


try:
    _POSTGRES = PostgresContainer("postgres:16-alpine")
    _POSTGRES.start()
    os.environ["postgres_url"] = _dsn_asyncpg(_POSTGRES.get_connection_url())
    os.environ.setdefault("main_service_url", "http://127.0.0.1:9")
    _DATABASE_READY = True
except (DockerException, ConnectionError, OSError):
    os.environ["postgres_url"] = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:65534/__pytest_placeholder__"
    )
    os.environ.setdefault("main_service_url", "http://127.0.0.1:9")



pytestmark = pytest.mark.skipif(
    not _DATABASE_READY,
    reason="Нужен запущенный Docker (Testcontainers Postgres).",
)


@pytest.fixture(scope="session", autouse=True)
async def database_schema() -> None:
    """Схема и остановка контейнера в одном event loop с async-тестами (без asyncio.run при импорте)."""
    if not _DATABASE_READY:
        yield
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    if _POSTGRES is not None:
        _POSTGRES.stop()


@pytest.fixture(scope="session")
def app(database_schema):
    return get_app()


@pytest.fixture
async def async_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def biography_session(database_schema):
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def mock_author_service_client(monkeypatch: pytest.MonkeyPatch) -> None:
    async def validate_author(self, author_id): 
        return author_id

    monkeypatch.setattr(AuthorServiceClient, "validate_author", validate_author)
