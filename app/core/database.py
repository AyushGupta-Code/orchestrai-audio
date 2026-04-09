"""SQLite helpers used by the stub pipeline."""

from __future__ import annotations

import sqlite3

from app.core.config import DATABASE_PATH, ensure_data_directories


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row access by column name."""
    ensure_data_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the minimal database schema used by the current phase.

    A single table is enough for now because the goal is clarity, not a final
    normalized schema.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                request_text TEXT NOT NULL,
                request_type TEXT NOT NULL,
                title TEXT NOT NULL,
                total_duration_minutes INTEGER NOT NULL,
                plan_json TEXT NOT NULL,
                routing_json TEXT NOT NULL DEFAULT '{}',
                validation_json TEXT NOT NULL DEFAULT '{}',
                segment_artifacts_json TEXT NOT NULL,
                final_artifact_path TEXT NOT NULL
            )
            """
        )
        ensure_routing_json_column(connection)
        ensure_validation_json_column(connection)
        connection.commit()


def ensure_routing_json_column(connection: sqlite3.Connection) -> None:
    """Add the `routing_json` column for older local databases if needed."""
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(runs)")
    }
    if "routing_json" not in existing_columns:
        connection.execute(
            """
            ALTER TABLE runs
            ADD COLUMN routing_json TEXT NOT NULL DEFAULT '{}'
            """
        )


def ensure_validation_json_column(connection: sqlite3.Connection) -> None:
    """Add the `validation_json` column for older local databases if needed."""
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(runs)")
    }
    if "validation_json" not in existing_columns:
        connection.execute(
            """
            ALTER TABLE runs
            ADD COLUMN validation_json TEXT NOT NULL DEFAULT '{}'
            """
        )
