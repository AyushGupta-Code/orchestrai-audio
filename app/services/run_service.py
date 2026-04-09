"""High-level orchestration wrappers for the pipeline.

Phase 3 routes the main execution path through LangGraph, but the helper
functions in this module remain useful because graph nodes reuse them.
"""

from __future__ import annotations

from uuid import uuid4

from app.models.schemas import AudioRequestPlan, BackendRoutingDecision, RunRecord, SegmentPlan
from app.services.cache_service import cache_run_record, get_cached_run_record
from app.services.music_service import create_ambient_artifact, create_music_artifact
from app.services.voice_service import create_voice_artifact


def run_pipeline(request_text: str) -> RunRecord:
    """Run the pipeline through the LangGraph workflow and return the saved run."""
    cached_run_record = get_cached_run_record(request_text)
    if cached_run_record is not None:
        return cached_run_record

    # Imported here to avoid a circular import: the workflow reuses helper
    # functions from this module, and this wrapper calls back into the workflow.
    from app.graph.workflow import run_workflow

    final_state = run_workflow(request_text)
    run_record = final_state["run_record"]
    cache_run_record(request_text, run_record)
    return run_record


def generate_run_id() -> str:
    """Create a short deterministic-looking run id."""
    return f"run_{uuid4().hex[:12]}"


def generate_segment_artifacts(
    run_id: str,
    plan: AudioRequestPlan,
    routing: BackendRoutingDecision,
) -> list[str]:
    """Generate one placeholder artifact per segment.

    The selection logic stays explicit so a reader can see how the segment type
    maps to a placeholder generation backend.
    """
    artifact_paths: list[str] = []

    for segment in plan.segments:
        artifact_paths.append(generate_artifact_for_segment(run_id, segment, routing))

    return artifact_paths


def generate_artifact_for_segment(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Create the most relevant placeholder artifact for one segment."""
    if segment.segment_type in {"ambient"}:
        return create_ambient_artifact(run_id, segment, routing)

    if segment.narration_text:
        return create_voice_artifact(run_id, segment, routing)

    return create_music_artifact(run_id, segment, routing)
