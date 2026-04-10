"""Voice generation helpers.

Phase 8 keeps the stub text output path, but can optionally use a simple local
text-to-speech backend if `pyttsx3` is installed and enabled.
"""

from __future__ import annotations

import io
import importlib.util
import math
import struct
import wave

from app.core.config import ENABLE_REAL_VOICE
from app.models.schemas import BackendRoutingDecision, SegmentPlan
from app.storage.artifacts import write_artifact_bytes, write_artifact_text


def create_voice_artifact(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Create a narration artifact for one segment.

    Priority order:
    1) optional local pyttsx3 backend when enabled and available
    2) lightweight built-in WAV cue synthesis
    3) text fallback when WAV synthesis fails unexpectedly
    """
    if should_use_real_voice_backend(routing):
        real_artifact_path = try_create_pyttsx3_voice_artifact(run_id, segment, routing)
        if real_artifact_path:
            return real_artifact_path

    fallback_wav_path = create_builtin_voice_cue_wav(run_id, segment, routing)
    if fallback_wav_path:
        return fallback_wav_path

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


def create_builtin_voice_cue_wav(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str | None:
    """Create a tiny local WAV cue when TTS is unavailable."""
    try:
        duration_seconds = min(max(segment.duration_minutes, 1), 6)
        wav_bytes = build_voice_cue_wave_bytes(duration_seconds=duration_seconds)
        file_name = f"{segment.segment_id}_{segment.segment_type}.wav"
        return write_artifact_bytes(run_id, file_name, wav_bytes)
    except Exception:
        return None


def build_voice_cue_wave_bytes(duration_seconds: int) -> bytes:
    """Build a low-volume mono PCM WAV cue with short beeps."""
    sample_rate = 22050
    frame_count = sample_rate * duration_seconds
    cue_frequency = 660
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for frame_index in range(frame_count):
            second_offset = frame_index / sample_rate
            in_beep_window = (second_offset % 1.0) < 0.18
            amplitude = 0.16 if in_beep_window else 0.02
            sample = amplitude * math.sin(2 * math.pi * cue_frequency * second_offset)
            frames.extend(struct.pack("<h", int(sample * 32767)))
        wav_file.writeframes(bytes(frames))

    return buffer.getvalue()
