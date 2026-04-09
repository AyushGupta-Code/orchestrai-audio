"""Optional request-result caching helpers.

The cache is intentionally file-based and simple to inspect. A normalized
request string maps to a JSON file containing the saved run record. If caching
is disabled, these helpers quietly do nothing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.core.config import CACHE_DIR, ENABLE_REQUEST_CACHE, ensure_data_directories
from app.models.schemas import RunRecord


def get_cached_run_record(request_text: str) -> RunRecord | None:
    """Return a cached run record for the request, if caching is enabled."""
    if not ENABLE_REQUEST_CACHE:
        return None

    cache_path = get_cache_path(request_text)
    if not cache_path.exists():
        return None

    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    return RunRecord.from_dict(payload)


def cache_run_record(request_text: str, run_record: RunRecord) -> None:
    """Persist one run record to the local request cache."""
    if not ENABLE_REQUEST_CACHE:
        return

    cache_path = get_cache_path(request_text)
    cache_path.write_text(
        json.dumps(run_record.to_dict(), indent=2),
        encoding="utf-8",
    )


def get_cache_path(request_text: str) -> Path:
    """Return the cache file path for a normalized request string."""
    ensure_data_directories()
    normalized_request = " ".join(request_text.strip().split()).lower()
    cache_key = hashlib.sha256(normalized_request.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{cache_key}.json"
