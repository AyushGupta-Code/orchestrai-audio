"""Lightweight tests for validation behavior."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.planning_service import build_audio_plan
from app.services.request_parser import parse_request
from app.services.validation_service import validate_outputs


class ValidationServiceTests(unittest.TestCase):
    """Verify that validation passes and fails for the expected reasons."""

    def test_validation_passes_when_files_exist(self) -> None:
        plan = build_audio_plan(parse_request("Generate 2 hours of calm rain ambience for studying"))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            segment_artifact = temp_path / "segment-01.txt"
            final_artifact = temp_path / "final.txt"
            segment_artifact.write_text("segment", encoding="utf-8")
            final_artifact.write_text("final", encoding="utf-8")

            result = validate_outputs(
                plan=plan,
                segment_artifacts=[str(segment_artifact)],
                final_artifact_path=str(final_artifact),
                retry_count=0,
            )

        self.assertTrue(result.passed)
        self.assertEqual(result.failures, [])

    def test_validation_fails_when_artifacts_are_missing(self) -> None:
        plan = build_audio_plan(parse_request("Turn this chapter into an audiobook with fitting background music"))
        result = validate_outputs(
            plan=plan,
            segment_artifacts=["/tmp/does-not-exist-segment.txt"],
            final_artifact_path="/tmp/does-not-exist-final.txt",
            retry_count=1,
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.retry_count, 1)
        self.assertTrue(any("missing" in failure.lower() for failure in result.failures))


if __name__ == "__main__":
    unittest.main()

