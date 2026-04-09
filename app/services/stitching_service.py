"""Stub stitching service for combining segment placeholders."""

from __future__ import annotations

from app.models.schemas import AudioRequestPlan, BackendRoutingDecision
from app.storage.artifacts import write_artifact_text


def create_final_artifact(
    run_id: str,
    plan: AudioRequestPlan,
    routing: BackendRoutingDecision,
    segment_artifact_paths: list[str],
) -> str:
    """Write a placeholder final artifact that lists all segment outputs."""
    lines = [
        "artifact_kind: stub_final_mix",
        f"title: {plan.title}",
        f"request_type: {plan.request_type}",
        f"total_duration_minutes: {plan.total_duration_minutes}",
        f"mood: {plan.mood}",
        f"style: {plan.style}",
        f"pacing: {plan.pacing}",
        f"break_pattern: {plan.break_pattern or 'None'}",
        f"output_strategy: {plan.output_strategy}",
        f"music_backend_name: {routing.music_backend_name or 'None'}",
        f"voice_backend_name: {routing.voice_backend_name or 'None'}",
        f"stitching_strategy: {routing.stitching_strategy}",
        f"routing_reason: {routing.routing_reason}",
        "segments:",
    ]
    lines.extend(f"- {path}" for path in segment_artifact_paths)
    return write_artifact_text(run_id, "final_mix.txt", lines)
