"""Unit tests for SQLAlchemy persistence primitives."""

from pathlib import Path

from sqlalchemy import Engine, text

from bridge_surface.persistence import (
    Base,
    create_database_engine,
    create_session_factory,
    session_scope,
)


def test_declarative_base_starts_without_domain_tables() -> None:
    assert not Base.metadata.tables


def test_engine_is_lazy_and_session_can_reach_sqlite(
    sqlite_database_path: Path,
    sqlite_database_url: str,
) -> None:
    engine = create_database_engine(sqlite_database_url)

    try:
        assert not sqlite_database_path.exists()

        factory = create_session_factory(engine)
        with session_scope(factory) as session:
            assert session.scalar(text("SELECT 1")) == 1
            assert session.autoflush is False
            assert session.expire_on_commit is False

        assert sqlite_database_path.exists()
    finally:
        engine.dispose()


def test_isolated_engine_contains_no_application_tables(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        table_count = connection.scalar(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'")
        )

    assert table_count == 0
