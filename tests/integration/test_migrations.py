"""Integration tests for the empty Alembic migration lifecycle."""

import os
import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect


def current_revision(engine: Engine) -> str | None:
    """Read the current Alembic revision from an isolated database."""

    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def test_empty_baseline_is_the_only_migration_head(alembic_config: Config) -> None:
    scripts = ScriptDirectory.from_config(alembic_config)

    assert scripts.get_heads() == ["0001_empty_baseline"]
    assert scripts.get_base() == "0001_empty_baseline"


def test_migration_upgrades_to_head_and_downgrades_to_base(
    alembic_config: Config,
    database_engine: Engine,
) -> None:
    command.upgrade(alembic_config, "head")

    assert current_revision(database_engine) == "0001_empty_baseline"
    assert inspect(database_engine).get_table_names() == ["alembic_version"]

    command.downgrade(alembic_config, "base")

    assert current_revision(database_engine) is None
    assert inspect(database_engine).get_table_names() == ["alembic_version"]

    command.upgrade(alembic_config, "head")
    assert current_revision(database_engine) == "0001_empty_baseline"


def test_importing_application_does_not_create_a_database(
    sqlite_database_path: Path,
    sqlite_database_url: str,
) -> None:
    environment = os.environ.copy()
    environment["BRIDGE_DATABASE_URL"] = sqlite_database_url

    result = subprocess.run(
        [sys.executable, "-c", "import apps.api.main"],
        check=False,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[2],
        env=environment,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not sqlite_database_path.exists()
