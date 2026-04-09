"""Simple routing helpers for Phase 4.

The routing logic stays intentionally obvious. We map the parsed request type
directly to a workflow path name so the graph can branch in a readable way.
"""

from __future__ import annotations

from app.models.schemas import AudioRequest


SUPPORTED_WORKFLOW_PATHS = {
    "music_session",
    "pomodoro_session",
    "audiobook",
    "ambient_session",
    "custom_timeline",
}


def choose_workflow_path(audio_request: AudioRequest) -> str:
    """Return the workflow path for the parsed request.

    For Phase 4 the workflow path is the same as the parsed request type.
    Keeping this in a dedicated service makes later routing logic easier to
    upgrade without forcing graph changes everywhere else.
    """
    if audio_request.request_type not in SUPPORTED_WORKFLOW_PATHS:
        return "custom_timeline"
    return audio_request.request_type

