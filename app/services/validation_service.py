"""Validation helpers for the stub pipeline.

Phase 7 keeps validation intentionally small and explicit. The goal is to
check the obvious things after generation and, if needed, allow one or two
simple retries without introducing complex retry machinery.
"""

from __future__ import annotations

from pathlib import Path

from app.models.schemas import AudioRequestPlan, ValidationResult


def validate_outputs(
    plan: AudioRequestPlan,
    segment_artifacts: list[str],
    final_artifact_path: str,
    retry_count: int,
) -> ValidationResult:
    """Validate that the generated output looks complete enough to keep."""
    checks: list[str] = []
    failures: list[str] = []

    if plan.segments:
        checks.append("Plan contains at least one segment.")
    else:
        failures.append("Plan does not contain any segments.")

    if segment_artifacts:
        checks.append("Segment artifact path list is not empty.")
    else:
        failures.append("Segment artifact path list is empty.")

    if all(path.strip() for path in segment_artifacts):
        checks.append("Segment artifact paths are not empty strings.")
    else:
        failures.append("One or more segment artifact paths are empty.")

    missing_segment_artifacts = [
        path for path in segment_artifacts if path.strip() and not Path(path).exists()
    ]
    if missing_segment_artifacts:
        failures.append(
            "Expected segment artifacts are missing: "
            + ", ".join(missing_segment_artifacts)
        )
    else:
        checks.append("Expected segment artifact files exist.")

    if final_artifact_path.strip():
        checks.append("Final artifact path is not empty.")
    else:
        failures.append("Final artifact path is empty.")

    if final_artifact_path.strip() and Path(final_artifact_path).exists():
        checks.append("Final stitched artifact file exists.")
    else:
        failures.append("Final stitched artifact file is missing.")

    return ValidationResult(
        passed=not failures,
        checks=checks,
        failures=failures,
        retry_count=retry_count,
    )
