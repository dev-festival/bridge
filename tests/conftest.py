"""Shared isolated database and migration fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from bridge_surface.persistence import (
    create_database_engine,
    create_session_factory,
    session_scope,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def anyio_backend() -> str:
    """Keep async HTTP tests on the installed asyncio backend."""

    return "asyncio"


@pytest.fixture
def sqlite_database_path(tmp_path: Path) -> Path:
    """Return a unique database path for one test."""

    return tmp_path / "bridge_surface_test.db"


@pytest.fixture
def sqlite_database_url(sqlite_database_path: Path) -> str:
    """Return a SQLAlchemy URL for the isolated test database."""

    return f"sqlite:///{sqlite_database_path.as_posix()}"


@pytest.fixture
def database_engine(sqlite_database_url: str) -> Iterator[Engine]:
    """Yield an engine tied only to the current test's database."""

    engine = create_database_engine(sqlite_database_url)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def alembic_config(sqlite_database_url: str) -> Config:
    """Return an Alembic configuration targeting the isolated test database."""

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", (PROJECT_ROOT / "migrations").as_posix())
    config.set_main_option("sqlalchemy.url", sqlite_database_url)
    return config


@pytest.fixture
def migrated_database_engine(alembic_config: Config, database_engine: Engine) -> Engine:
    """Return an isolated engine after applying all committed migrations."""

    command.upgrade(alembic_config, "head")
    return database_engine


@pytest.fixture
def database_session(migrated_database_engine: Engine) -> Iterator[Session]:
    """Yield a session connected to a fully migrated isolated database."""

    factory = create_session_factory(migrated_database_engine)
    with session_scope(factory) as session:
        yield session
