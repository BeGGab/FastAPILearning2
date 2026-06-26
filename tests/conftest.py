from __future__ import annotations

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
from src.models.authors.model import Base
from alembic.config import Config
from alembic import command
from src.config import Settings

settings = Settings()

from src.application import get_app  
from src.db import async_session_maker, engine

_POSTGRES: PostgresContainer | None = None



def _bootstrap_postgres() -> None:
    global _POSTGRES

    _POSTGRES = PostgresContainer("postgres:16-alpine")
    _POSTGRES.start()
    os.environ["postgres_url"] = _POSTGRES.get_connection_url().replace("postgresql", "postgresql+asyncpg")
    os.environ.setdefault("main_service_url", "http://127.0.0.1:9")


_bootstrap_postgres()


def _run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.postgres_url))
    command.upgrade(alembic_cfg, "head")

def pytest_sessionfinish(session, exitstatus):  
    global _POSTGRES
    if _POSTGRES is not None:
        _POSTGRES.stop()
        _POSTGRES = None
    engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app():
    _run_migrations()
    return get_app()


@pytest_asyncio.fixture(loop_scope="session")
async def async_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session")
async def biography_session():
    async with async_session_maker() as session:
        yield session
