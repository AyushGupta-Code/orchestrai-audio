"""Command-line entry point for the current stub pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path


# When this script is executed directly, Python adds the `scripts/` directory
# to sys.path, not the repository root. We insert the repo root so `app.*`
# imports work without asking the user to modify PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.run_service import run_pipeline


def main() -> int:
    """Accept a freeform request, run the pipeline, and print a summary."""
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/run_demo.py "Create a calm study session."')
        return 1

    request_text = " ".join(sys.argv[1:])
    run_record = run_pipeline(request_text)

    print("Structured plan summary:")
    print(json.dumps(run_record.plan.to_dict(), indent=2))
    print()
    print(f"Saved run_id: {run_record.run_id}")
    print(f"Final artifact: {run_record.final_artifact_path}")
    print("Segment artifacts:")
    for artifact_path in run_record.segment_artifacts:
        print(f"- {artifact_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
