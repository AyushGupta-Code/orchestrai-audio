"""Small configuration helpers for local paths and optional integrations.

Everything writes to the local repository so the project is easy to inspect.
Phase 8 adds a few environment-controlled feature flags so optional local
integrations can be turned on without breaking the stub fallback behavior.
"""

from __future__ import annotations

import os
from pathlib import Path


# This file lives at app/core/config.py, so parent[2] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
CACHE_DIR = DATA_DIR / "cache"
DATABASE_PATH = DATA_DIR / "orchestrai_audio.db"
TEMPLATE_LIBRARY_PATH = REPO_ROOT / "templates" / "plan_templates.json"


def env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean environment flag in a forgiving way."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


# Optional real integration flags.
# These all default to False so the safe stub path remains the default behavior.
ENABLE_REAL_REQUEST_UNDERSTANDING = env_flag("ORCH_AUDIO_ENABLE_REAL_REQUEST_UNDERSTANDING", default=False)
ENABLE_REAL_VOICE = env_flag("ORCH_AUDIO_ENABLE_REAL_VOICE", default=False)
ENABLE_REAL_MUSIC = env_flag("ORCH_AUDIO_ENABLE_REAL_MUSIC", default=False)
ENABLE_TEMPLATE_RETRIEVAL = env_flag("ORCH_AUDIO_ENABLE_TEMPLATE_RETRIEVAL", default=False)
ENABLE_REQUEST_CACHE = env_flag("ORCH_AUDIO_ENABLE_REQUEST_CACHE", default=False)


# Optional model or backend names.
# These are plain strings so later phases can reuse them without changing the
# public configuration shape.
REQUEST_SENTIMENT_MODEL = os.getenv("ORCH_AUDIO_REQUEST_SENTIMENT_MODEL", "")
VOICE_BACKEND_PREFERENCE = os.getenv("ORCH_AUDIO_VOICE_BACKEND", "pyttsx3")
MUSIC_BACKEND_PREFERENCE = os.getenv("ORCH_AUDIO_MUSIC_BACKEND", "wave_tone")


def ensure_data_directories() -> None:
    """Create local storage directories if they do not exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
