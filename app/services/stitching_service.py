"""Stitching helpers for combining generated segment artifacts."""

from __future__ import annotations

import io
import wave
from pathlib import Path

from app.models.schemas import AudioRequestPlan, BackendRoutingDecision
from app.storage.artifacts import write_artifact_bytes, write_artifact_text


def create_final_artifact(
    run_id: str,
    plan: AudioRequestPlan,
    routing: BackendRoutingDecision,
    segment_artifact_paths: list[str],
) -> str:
    """Create a final run artifact.

    If one or more segment artifacts are WAV files with matching audio
    parameters, this function concatenates the available WAV segments into
    `final_mix.wav`. Otherwise it falls back to a plain-text manifest so the
    run remains inspectable.
    """
    concatenated_wav_path = try_create_concatenated_wav(run_id, segment_artifact_paths)
    if concatenated_wav_path:
        return concatenated_wav_path

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


def try_create_concatenated_wav(run_id: str, segment_artifact_paths: list[str]) -> str | None:
    """Concatenate segment WAV files into one final WAV artifact.

    Returns:
        Absolute path to `final_mix.wav` when concatenation succeeds, else None.
    """
    if not segment_artifact_paths:
        return None

    wav_paths = [Path(path) for path in segment_artifact_paths if Path(path).suffix.lower() == ".wav"]
    if not wav_paths:
        return None

    try:
        with wave.open(str(wav_paths[0]), "rb") as first_wav:
            nchannels = first_wav.getnchannels()
            sampwidth = first_wav.getsampwidth()
            framerate = first_wav.getframerate()
            combined_frames = [first_wav.readframes(first_wav.getnframes())]

        for path in wav_paths[1:]:
            with wave.open(str(path), "rb") as wav_file:
                if (
                    wav_file.getnchannels() != nchannels
                    or wav_file.getsampwidth() != sampwidth
                    or wav_file.getframerate() != framerate
                ):
                    return None
                combined_frames.append(wav_file.readframes(wav_file.getnframes()))

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as final_wav:
            final_wav.setnchannels(nchannels)
            final_wav.setsampwidth(sampwidth)
            final_wav.setframerate(framerate)
            final_wav.writeframes(b"".join(combined_frames))

        return write_artifact_bytes(run_id, "final_mix.wav", buffer.getvalue())
    except Exception:
        return None
