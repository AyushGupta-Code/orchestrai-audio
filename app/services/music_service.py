"""Music and ambient generation helpers.

Phase 8 keeps the stub text output path, but can also generate simple local
WAV files when the optional real-music flag is enabled. The real path is still
deliberately minimal: it synthesizes plain tones with the standard library.
"""

from __future__ import annotations

import io
import math
import struct
import wave

from app.core.config import ENABLE_REAL_MUSIC
from app.models.schemas import BackendRoutingDecision, SegmentPlan
from app.storage.artifacts import write_artifact_bytes, write_artifact_text


def create_music_artifact(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Write a placeholder music artifact for one segment."""
    if should_use_real_music_backend(routing):
        return create_real_music_wav(run_id, segment, routing)

    file_name = f"{segment.segment_id}_{segment.segment_type}.txt"
    return write_artifact_text(
        run_id,
        file_name,
        [
            "artifact_kind: stub_music",
            f"music_backend_name: {routing.music_backend_name or 'None'}",
            f"segment_id: {segment.segment_id}",
            f"name: {segment.name}",
            f"duration_minutes: {segment.duration_minutes}",
            f"purpose: {segment.purpose}",
            f"mood: {segment.mood}",
            f"style: {segment.style}",
            f"music_prompt: {segment.music_prompt or 'None'}",
            f"routing_reason: {routing.routing_reason}",
        ],
    )


def create_ambient_artifact(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Write a placeholder ambience artifact for one segment."""
    if should_use_real_music_backend(routing):
        return create_real_ambient_wav(run_id, segment, routing)

    file_name = f"{segment.segment_id}_{segment.segment_type}.txt"
    return write_artifact_text(
        run_id,
        file_name,
        [
            "artifact_kind: stub_ambient",
            f"music_backend_name: {routing.music_backend_name or 'None'}",
            f"segment_id: {segment.segment_id}",
            f"name: {segment.name}",
            f"duration_minutes: {segment.duration_minutes}",
            f"purpose: {segment.purpose}",
            f"mood: {segment.mood}",
            f"style: {segment.style}",
            f"ambient_prompt: {segment.ambient_prompt or 'None'}",
            f"routing_reason: {routing.routing_reason}",
        ],
    )


def should_use_real_music_backend(routing: BackendRoutingDecision) -> bool:
    """Return True when the selected backend is the simple local WAV backend."""
    return ENABLE_REAL_MUSIC and routing.music_backend_name == "wave_tone_backend"


def create_real_music_wav(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Generate a very small synthetic WAV file for a music segment.

    This is intentionally basic. The goal is to create a real audio file
    without adding heavy dependencies or fragile model integrations.
    """
    duration_seconds = min(max(segment.duration_minutes * 2, 2), 12)
    wav_bytes = build_wave_bytes(
        duration_seconds=duration_seconds,
        frequency=pick_frequency(segment),
        amplitude=0.28,
    )
    file_name = f"{segment.segment_id}_{segment.segment_type}.wav"
    return write_artifact_bytes(run_id, file_name, wav_bytes)


def create_real_ambient_wav(
    run_id: str,
    segment: SegmentPlan,
    routing: BackendRoutingDecision,
) -> str:
    """Generate a simple low-frequency WAV file for an ambient segment."""
    duration_seconds = min(max(segment.duration_minutes * 2, 2), 12)
    wav_bytes = build_wave_bytes(
        duration_seconds=duration_seconds,
        frequency=max(pick_frequency(segment) // 2, 110),
        amplitude=0.18,
    )
    file_name = f"{segment.segment_id}_{segment.segment_type}.wav"
    return write_artifact_bytes(run_id, file_name, wav_bytes)


def build_wave_bytes(duration_seconds: int, frequency: int, amplitude: float) -> bytes:
    """Build a mono PCM WAV payload using only the Python standard library."""
    sample_rate = 22050
    frame_count = sample_rate * duration_seconds
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for frame_index in range(frame_count):
            sample = amplitude * math.sin(2 * math.pi * frequency * (frame_index / sample_rate))
            frames.extend(struct.pack("<h", int(sample * 32767)))
        wav_file.writeframes(bytes(frames))

    return buffer.getvalue()


def pick_frequency(segment: SegmentPlan) -> int:
    """Pick a stable tone frequency from segment mood and style."""
    if segment.mood in {"calm", "gentle", "welcoming"}:
        return 220
    if segment.mood in {"focused", "balanced"}:
        return 330
    if segment.mood in {"energetic", "uplifting", "encouraging"}:
        return 440
    return 275
