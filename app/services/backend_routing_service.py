"""Simple backend routing helpers for Phase 6.

The project still uses stub generation, so the selected backend names are also
stub names. The point of this layer is to make backend selection explicit,
inspectable, and easy to replace later with real integrations.
"""

from __future__ import annotations

import importlib.util

from app.core.config import ENABLE_REAL_VOICE, MUSIC_BACKEND_PREFERENCE, VOICE_BACKEND_PREFERENCE
from app.models.schemas import AudioRequestPlan, BackendRoutingDecision


def choose_backends(plan: AudioRequestPlan) -> BackendRoutingDecision:
    """Choose backend names and stitching strategy from the structured plan."""
    music_backend_name = choose_music_backend_name(plan)
    voice_backend_name = choose_voice_backend_name(plan)

    if plan.request_type == "audiobook":
        return BackendRoutingDecision(
            music_backend_name=music_backend_name,
            voice_backend_name=voice_backend_name,
            stitching_strategy="narration_first_mix",
            routing_reason=build_routing_reason(
                "Audiobook requests need both narration and supporting music.",
                music_backend_name,
                voice_backend_name,
            ),
        )

    if plan.request_type == "music_session":
        return BackendRoutingDecision(
            music_backend_name=music_backend_name,
            voice_backend_name=None,
            stitching_strategy="music_segment_concat",
            routing_reason=build_routing_reason(
                "Music sessions only need music generation and simple segment stitching.",
                music_backend_name,
                None,
            ),
        )

    if plan.request_type == "ambient_session":
        return BackendRoutingDecision(
            music_backend_name=music_backend_name,
            voice_backend_name=None,
            stitching_strategy="ambient_layered_stitch",
            routing_reason=build_routing_reason(
                "Ambient sessions focus on ambience and skip narration generation.",
                music_backend_name,
                None,
            ),
        )

    if plan.request_type == "pomodoro_session":
        return BackendRoutingDecision(
            music_backend_name=music_backend_name,
            voice_backend_name=voice_backend_name,
            stitching_strategy="alternating_focus_break_mix",
            routing_reason=build_routing_reason(
                "Pomodoro sessions benefit from music plus short voice cues for transitions.",
                music_backend_name,
                voice_backend_name,
            ),
        )

    return BackendRoutingDecision(
        music_backend_name=music_backend_name,
        voice_backend_name=voice_backend_name,
        stitching_strategy="guided_timeline_mix",
        routing_reason=build_routing_reason(
            "Custom timelines usually need both musical support and guided voice moments.",
            music_backend_name,
            voice_backend_name,
        ),
    )


def choose_music_backend_name(plan: AudioRequestPlan) -> str | None:
    """Choose a music backend name.

    The built-in `wave_tone` backend uses only the Python standard library and
    can run by default without extra model downloads.
    """
    if not plan.needs_music and plan.request_type != "ambient_session":
        return None

    if MUSIC_BACKEND_PREFERENCE == "wave_tone":
        return "wave_tone_backend"

    if plan.request_type == "ambient_session":
        return "stub_ambient_texture_backend"
    if plan.request_type == "music_session":
        return "stub_music_session_backend"
    if plan.request_type == "pomodoro_session":
        return "stub_focus_music_backend"
    return "stub_timeline_music_backend"


def choose_voice_backend_name(plan: AudioRequestPlan) -> str | None:
    """Choose a voice backend name while preserving safe stub fallback."""
    if not plan.needs_narration:
        return None

    if ENABLE_REAL_VOICE and VOICE_BACKEND_PREFERENCE == "pyttsx3" and has_pyttsx3():
        return "pyttsx3_voice_backend"

    if plan.request_type == "audiobook":
        return "stub_voice_narration_backend"
    return "stub_voice_cue_backend"


def has_pyttsx3() -> bool:
    """Return True if the optional `pyttsx3` package is available locally."""
    return importlib.util.find_spec("pyttsx3") is not None


def build_routing_reason(
    base_reason: str,
    music_backend_name: str | None,
    voice_backend_name: str | None,
) -> str:
    """Create a readable routing explanation for saved metadata."""
    details = [base_reason]
    details.append(f"Music backend: {music_backend_name or 'none'}.")
    details.append(f"Voice backend: {voice_backend_name or 'none'}.")
    return " ".join(details)
