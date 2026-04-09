"""Helpers for writing local placeholder artifact files."""

from __future__ import annotations

from pathlib import Path

from app.core.config import ARTIFACTS_DIR, ensure_data_directories


def get_run_artifact_directory(run_id: str) -> Path:
    """Return the folder where one run stores its artifacts."""
    ensure_data_directories()
    run_directory = ARTIFACTS_DIR / run_id
    run_directory.mkdir(parents=True, exist_ok=True)
    return run_directory


def write_artifact_text(run_id: str, file_name: str, lines: list[str]) -> str:
    """Write a text artifact and return the absolute path as a string.

    Phase 1 uses text files to simulate generated audio files.
    That makes the flow easy to inspect without needing real audio tooling.
    """
    artifact_path = get_run_artifact_directory(run_id) / file_name
    artifact_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(artifact_path)


def write_artifact_bytes(run_id: str, file_name: str, payload: bytes) -> str:
    """Write a binary artifact such as a WAV file and return its path."""
    artifact_path = get_run_artifact_directory(run_id) / file_name
    artifact_path.write_bytes(payload)
    return str(artifact_path)
