"""Integration tests for the local User schema migration."""

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect


def test_user_migration_upgrades_and_downgrades_cleanly(
    alembic_config: Config,
    database_engine: Engine,
) -> None:
    command.upgrade(alembic_config, "0001_empty_baseline")
    assert not inspect(database_engine).has_table("users")

    command.upgrade(alembic_config, "0002_create_users")

    inspector = inspect(database_engine)
    assert inspector.has_table("users")
    assert {column["name"] for column in inspector.get_columns("users")} == {
        "id",
        "display_name",
        "preferred_language",
        "created_at",
        "updated_at",
    }
    assert inspector.get_pk_constraint("users")["constrained_columns"] == ["id"]
    assert {constraint["name"] for constraint in inspector.get_check_constraints("users")} == {
        "ck_users_preferred_language"
    }

    command.downgrade(alembic_config, "0001_empty_baseline")
    assert not inspect(database_engine).has_table("users")
