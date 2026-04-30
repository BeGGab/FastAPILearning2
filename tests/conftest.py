from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

import pytest
import pytest_asyncio
from docker.errors import DockerException
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
import src.models.authors.model  

from src.application import get_app  
from src.models.core.db import Base, async_session_maker, engine

_POSTGRES: PostgresContainer | None = None
_DATABASE_READY = False


def _dsn_asyncpg(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "postgresql+asyncpg":
        out = url
    elif parsed.scheme in ("postgresql", "postgres") or parsed.scheme.startswith("postgresql+"):
        path = parsed.path or "/"
        out = urlunparse(("postgresql+asyncpg", parsed.netloc, path, "", "", ""))
    else:
        return url
    parsed = urlparse(out)
    if parsed.hostname in ("localhost", "::1"):
        port = f":{parsed.port}" if parsed.port else ""
        auth = ""
        if parsed.username is not None:
            auth = parsed.username
            if parsed.password is not None:
                auth += f":{parsed.password}"
            auth += "@"
        netloc = f"{auth}127.0.0.1{port}"
        out = urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))
    return out


def _bootstrap_postgres() -> None:
    global _POSTGRES, _DATABASE_READY
    try:
        _POSTGRES = PostgresContainer("postgres:16-alpine")
        _POSTGRES.start()
        os.environ["postgres_url"] = _dsn_asyncpg(_POSTGRES.get_connection_url())
        os.environ.setdefault("main_service_url", "http://127.0.0.1:9")
        _DATABASE_READY = True
    except (DockerException, ConnectionError, OSError):
        _POSTGRES = None
        _DATABASE_READY = False
        os.environ["postgres_url"] = (
            "postgresql+asyncpg://postgres:postgres@127.0.0.1:65534/__pytest_placeholder__"
        )
        os.environ.setdefault("main_service_url", "http://127.0.0.1:9")


_bootstrap_postgres()



def pytest_collection_modifyitems(config, items) -> None:  
    if not _DATABASE_READY:
        skip = pytest.mark.skip(
            reason="Нужен запущенный Docker (Testcontainers Postgres).",
        )
        for item in items:
            item.add_marker(skip)


def pytest_sessionfinish(session, exitstatus):  
    global _POSTGRES
    if _POSTGRES is not None:
        _POSTGRES.stop()
        _POSTGRES = None


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def database_schema() -> None:
    if not _DATABASE_READY:
        yield
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app(database_schema):
    return get_app()


@pytest_asyncio.fixture(loop_scope="session")
async def async_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session")
async def biography_session(database_schema):
    async with async_session_maker() as session:
        yield session
