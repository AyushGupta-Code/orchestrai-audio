"""Rule-based parsing from freeform text into a normalized request model."""

from __future__ import annotations

import importlib
import re

from app.core.config import ENABLE_REAL_REQUEST_UNDERSTANDING, REQUEST_SENTIMENT_MODEL
from app.models.schemas import AudioRequest


REQUEST_TYPES = {
    "music_session",
    "pomodoro_session",
    "audiobook",
    "ambient_session",
    "custom_timeline",
}


def parse_request(text: str) -> AudioRequest:
    """Parse a freeform request using simple keyword rules.

    This parser is intentionally deterministic. The goal is not to be smart;
    the goal is to produce a predictable request shape that later phases can
    replace with stronger parsing logic.
    """
    cleaned_text = " ".join(text.strip().split())
    request_type = classify_request_type(cleaned_text)
    total_duration_minutes = extract_total_duration_minutes(cleaned_text, request_type)
    title = build_title(cleaned_text, request_type)

    return AudioRequest(
        text=cleaned_text,
        request_type=request_type,
        title=title,
        total_duration_minutes=total_duration_minutes,
    )


def classify_request_type(text: str) -> str:
    """Classify the request using a small set of keyword checks."""
    lower_text = text.lower()

    if "custom timeline" in lower_text:
        return "custom_timeline"
    if any(keyword in lower_text for keyword in ["audiobook", "chapter", "narration", "narrate"]):
        return "audiobook"
    if "pomodoro" in lower_text:
        return "pomodoro_session"
    if any(keyword in lower_text for keyword in ["ambient", "ambience", "rain", "soundscape"]):
        return "ambient_session"
    if any(keyword in lower_text for keyword in ["timeline", "intro", "outro", "work block", "break block"]):
        return "custom_timeline"
    if any(keyword in lower_text for keyword in ["music", "jazz", "playlist", "session"]):
        return "music_session"

    # Music session is the safest default because it can represent a generic
    # audio block even when the wording is ambiguous.
    return "music_session"


def extract_total_duration_minutes(text: str, request_type: str) -> int:
    """Extract a rough total duration from the request, or use defaults."""
    lower_text = text.lower()

    hours_match = re.search(r"(\d+)\s*hours?", lower_text)
    if hours_match:
        return int(hours_match.group(1)) * 60

    minutes_match = re.search(r"(\d+)\s*minutes?", lower_text)
    if minutes_match:
        return int(minutes_match.group(1))

    default_minutes = {
        "music_session": 60,
        "pomodoro_session": 60,
        "audiobook": 30,
        "ambient_session": 120,
        "custom_timeline": 45,
    }
    return default_minutes[request_type]


def build_title(text: str, request_type: str) -> str:
    """Create a short human-readable title for the run."""
    prefixes = {
        "music_session": "Music Session",
        "pomodoro_session": "Pomodoro Session",
        "audiobook": "Audiobook Session",
        "ambient_session": "Ambient Session",
        "custom_timeline": "Custom Timeline",
    }
    snippet = text[:50].strip()
    if len(text) > 50:
        snippet += "..."
    return f"{prefixes[request_type]}: {snippet}"


def extract_pomodoro_pattern(text: str) -> tuple[int, int]:
    """Extract work and break lengths for a pomodoro request."""
    lower_text = text.lower()
    work_minutes = 25
    break_minutes = 5

    work_match = re.search(r"every\s+(\d+)\s*-\s*minute\s+pomodoro", lower_text)
    if not work_match:
        work_match = re.search(r"every\s+(\d+)\s*minute\s+pomodoro", lower_text)
    if work_match:
        work_minutes = int(work_match.group(1))

    break_match = re.search(r"(\d+)\s*-\s*minute\s+break", lower_text)
    if not break_match:
        break_match = re.search(r"(\d+)\s*minute\s+break", lower_text)
    if break_match:
        break_minutes = int(break_match.group(1))

    return work_minutes, break_minutes


def infer_mood_hint(text: str) -> str | None:
    """Optionally use a local sentiment model to suggest a mood.

    This stays optional on purpose. If the local dependency or model is missing,
    the function quietly returns `None` and the existing rule-based mood logic
    remains in control.
    """
    if not ENABLE_REAL_REQUEST_UNDERSTANDING:
        return None

    if not REQUEST_SENTIMENT_MODEL:
        return None

    try:
        transformers = importlib.import_module("transformers")
        pipeline = transformers.pipeline
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=REQUEST_SENTIMENT_MODEL,
            local_files_only=True,
        )
        result = sentiment_pipeline(text[:512])[0]
    except Exception:
        return None

    label = str(result.get("label", "")).lower()
    if "pos" in label:
        return "uplifting"
    if "neg" in label:
        return "somber"
    return "balanced"
