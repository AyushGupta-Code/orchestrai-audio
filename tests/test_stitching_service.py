"""Tests for final artifact stitching behavior."""

from __future__ import annotations

import wave
from pathlib import Path

from app.models.schemas import AudioRequestPlan, BackendRoutingDecision, SegmentPlan
from app.services.stitching_service import create_final_artifact
from app.storage.artifacts import write_artifact_text


def _make_plan() -> AudioRequestPlan:
    return AudioRequestPlan(
        request_type="music_session",
        title="Test Session",
        total_duration_minutes=10,
        mood="focused",
        style="jazz",
        pacing="steady",
        needs_music=True,
        needs_narration=False,
        needs_breaks=False,
        break_pattern=None,
        output_strategy="music_segment_concat",
        segments=[
            SegmentPlan(
                segment_id="segment-01",
                name="Music Block 1",
                segment_type="music",
                duration_minutes=5,
                purpose="Test",
                mood="focused",
                style="jazz",
                music_prompt="Prompt",
                narration_text=None,
                ambient_prompt=None,
                include_voice_cue=False,
            )
        ],
        notes=[],
    )


def _make_routing() -> BackendRoutingDecision:
    return BackendRoutingDecision(
        music_backend_name="wave_tone_backend",
        voice_backend_name=None,
        stitching_strategy="music_segment_concat",
        routing_reason="test",
    )


def _write_tiny_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes(b"\x00\x00" * 2205)


def test_create_final_artifact_concatenates_wav_segments(tmp_path: Path) -> None:
    wav_one = tmp_path / "segment-01.wav"
    wav_two = tmp_path / "segment-02.wav"
    _write_tiny_wav(wav_one)
    _write_tiny_wav(wav_two)

    final_path = create_final_artifact(
        run_id="run_test_wav_concat",
        plan=_make_plan(),
        routing=_make_routing(),
        segment_artifact_paths=[str(wav_one), str(wav_two)],
    )

    assert final_path.endswith("final_mix.wav")
    with wave.open(final_path, "rb") as final_wav:
        assert final_wav.getframerate() == 22050
        assert final_wav.getnchannels() == 1
        assert final_wav.getsampwidth() == 2
        assert final_wav.getnframes() == 4410


def test_create_final_artifact_falls_back_to_text_when_non_wav_present() -> None:
    run_id = "run_test_text_fallback"
    text_path = write_artifact_text(run_id, "segment-01_music.txt", ["stub"])

    final_path = create_final_artifact(
        run_id=run_id,
        plan=_make_plan(),
        routing=_make_routing(),
        segment_artifact_paths=[text_path],
    )

    assert final_path.endswith("final_mix.txt")


def test_create_final_artifact_uses_wav_when_mixed_segment_types(tmp_path: Path) -> None:
    wav_one = tmp_path / "segment-01.wav"
    _write_tiny_wav(wav_one)

    run_id = "run_test_mixed_paths"
    text_path = write_artifact_text(run_id, "segment-02_break_block.txt", ["stub"])

    final_path = create_final_artifact(
        run_id=run_id,
        plan=_make_plan(),
        routing=_make_routing(),
        segment_artifact_paths=[str(wav_one), text_path],
    )

    assert final_path.endswith("final_mix.wav")
