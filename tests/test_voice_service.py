"""Tests for voice artifact generation."""

from __future__ import annotations

import wave

from app.models.schemas import BackendRoutingDecision, SegmentPlan
from app.services.voice_service import create_voice_artifact


def _segment_with_narration() -> SegmentPlan:
    return SegmentPlan(
        segment_id="segment-voice-01",
        name="Break Cue",
        segment_type="break_block",
        duration_minutes=2,
        purpose="Cue a short break.",
        mood="gentle",
        style="reset",
        music_prompt=None,
        narration_text="Take a short break and reset.",
        ambient_prompt=None,
        include_voice_cue=True,
    )


def test_create_voice_artifact_generates_builtin_wav_when_tts_not_enabled() -> None:
    segment = _segment_with_narration()
    routing = BackendRoutingDecision(
        music_backend_name="wave_tone_backend",
        voice_backend_name="stub_voice_cue_backend",
        stitching_strategy="alternating_focus_break_mix",
        routing_reason="test",
    )

    artifact_path = create_voice_artifact("run_voice_wav_fallback", segment, routing)

    assert artifact_path.endswith(".wav")
    with wave.open(artifact_path, "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == 22050
