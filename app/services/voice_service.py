"""Voice generation helpers.

Phase 8 keeps the stub text output path, but can optionally use a simple local
text-to-speech backend if `pyttsx3` is installed and enabled.
"""

from __future__ import annotations

import importlib.util

from app.core.config import ENABLE_REAL_VOICE
from app.models.schemas import BackendRoutingDecision, SegmentPlan
from app.storage.artifacts import write_artifact_text


def create_voice_artifact(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Write a placeholder narration artifact for one segment."""
    if should_use_real_voice_backend(routing):
        real_artifact_path = try_create_pyttsx3_voice_artifact(run_id, segment, routing)
        if real_artifact_path:
            return real_artifact_path

    file_name = f"{segment.segment_id}_{segment.segment_type}.txt"
    return write_artifact_text(
        run_id,
        file_name,
        [
            "artifact_kind: stub_voice",
            f"voice_backend_name: {routing.voice_backend_name or 'None'}",
            f"segment_id: {segment.segment_id}",
            f"name: {segment.name}",
            f"duration_minutes: {segment.duration_minutes}",
            f"purpose: {segment.purpose}",
            f"mood: {segment.mood}",
            f"style: {segment.style}",
            f"include_voice_cue: {segment.include_voice_cue}",
            f"narration_text: {segment.narration_text or 'None'}",
            f"routing_reason: {routing.routing_reason}",
        ],
    )


def should_use_real_voice_backend(routing: BackendRoutingDecision) -> bool:
    """Return True when the selected backend is the optional local TTS path."""
    return (
        ENABLE_REAL_VOICE
        and routing.voice_backend_name == "pyttsx3_voice_backend"
        and importlib.util.find_spec("pyttsx3") is not None
    )


def try_create_pyttsx3_voice_artifact(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str | None:
    """Try to synthesize a local narration WAV file with `pyttsx3`.

    This function swallows backend-specific failures and returns `None` so the
    caller can fall back to the stub artifact path without breaking the run.
    """
    try:
        import pyttsx3
    except Exception:
        return None

    from app.storage.artifacts import get_run_artifact_directory

    output_path = get_run_artifact_directory(run_id) / f"{segment.segment_id}_{segment.segment_type}.wav"

    try:
        engine = pyttsx3.init()
        engine.save_to_file(
            segment.narration_text or segment.name,
            str(output_path),
        )
        engine.runAndWait()
        if output_path.exists():
            return str(output_path)
    except Exception:
        return None

    return None
