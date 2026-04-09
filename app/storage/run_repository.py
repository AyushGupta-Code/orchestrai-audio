"""Persistence helpers for saving pipeline runs in SQLite."""

from __future__ import annotations

import json

from app.core.database import get_connection, initialize_database
from app.models.schemas import RunRecord


def save_run_record(run_record: RunRecord) -> None:
    """Persist one run record into SQLite."""
    initialize_database()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id,
                created_at,
                request_text,
                request_type,
                title,
                total_duration_minutes,
                plan_json,
                routing_json,
                validation_json,
                segment_artifacts_json,
                final_artifact_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_record.run_id,
                run_record.created_at,
                run_record.request_text,
                run_record.request_type,
                run_record.title,
                run_record.total_duration_minutes,
                json.dumps(run_record.plan.to_dict(), indent=2),
                json.dumps(run_record.backend_routing.to_dict(), indent=2),
                json.dumps(run_record.validation_result.to_dict(), indent=2),
                json.dumps(run_record.segment_artifacts, indent=2),
                run_record.final_artifact_path,
            ),
        )
        connection.commit()
