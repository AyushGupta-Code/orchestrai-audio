"""Small verification script for the Phase 0 repository scaffold.

This script intentionally does not run any pipeline logic.
It only confirms that the expected folders exist so the repo
has a clean starting point for Phase 1.
"""

from __future__ import annotations

import json
from pathlib import Path


EXPECTED_DIRECTORIES = [
    "app/api",
    "app/core",
    "app/graph",
    "app/models",
    "app/services",
    "app/storage",
    "data/artifacts",
    "docs",
    "scripts",
    "tests",
]


def build_status() -> dict[str, object]:
    """Return a simple status summary for the scaffold."""
    repo_root = Path(__file__).resolve().parents[1]
    existing_directories = []

    for relative_path in EXPECTED_DIRECTORIES:
        directory_path = repo_root / relative_path
        if directory_path.exists():
            existing_directories.append(relative_path)

    return {
        "project": "orchestrai-audio",
        "phase": "Phase 0",
        "status": "ready for Phase 1" if len(existing_directories) == len(EXPECTED_DIRECTORIES) else "incomplete",
        "expected_directory_count": len(EXPECTED_DIRECTORIES),
        "existing_directory_count": len(existing_directories),
        "existing_directories": existing_directories,
    }


def main() -> None:
    """Print the scaffold status as formatted JSON."""
    print(json.dumps(build_status(), indent=2))


if __name__ == "__main__":
    main()

