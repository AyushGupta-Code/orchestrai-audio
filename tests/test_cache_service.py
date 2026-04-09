"""Tests for the request cache service."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models.schemas import AudioRequestPlan, BackendRoutingDecision, RunRecord, ValidationResult
from app.services.cache_service import get_cache_path


class CacheServiceTests(unittest.TestCase):
    """Verify the cache path is stable for the same request."""

    def test_cache_path_is_stable_for_same_request(self) -> None:
        first_path = get_cache_path("Generate 2 hours of calm rain ambience for studying")
        second_path = get_cache_path("Generate 2 hours of calm rain ambience for studying")
        self.assertEqual(first_path.name, second_path.name)

    def test_run_record_round_trip_from_dict(self) -> None:
        run_record = RunRecord(
            run_id="run_test",
            created_at="2026-01-01T00:00:00Z",
            request_text="Generate 2 hours of calm rain ambience for studying",
            request_type="ambient_session",
            title="Ambient Session: test",
            total_duration_minutes=120,
            plan=AudioRequestPlan(
                request_type="ambient_session",
                title="Ambient Session: test",
                total_duration_minutes=120,
                mood="calm",
                style="ambient",
                pacing="slow",
                needs_music=False,
                needs_narration=False,
                needs_breaks=False,
                segments=[],
                notes=[],
            ),
            backend_routing=BackendRoutingDecision(
                music_backend_name="stub_ambient_texture_backend",
                voice_backend_name=None,
                stitching_strategy="ambient_layered_stitch",
                routing_reason="test",
            ),
            validation_result=ValidationResult(
                passed=True,
                checks=["ok"],
                failures=[],
                retry_count=0,
            ),
            segment_artifacts=[],
            final_artifact_path="/tmp/final.txt",
        )

        rebuilt = RunRecord.from_dict(json.loads(json.dumps(run_record.to_dict())))
        self.assertEqual(rebuilt.run_id, "run_test")
        self.assertEqual(rebuilt.plan.request_type, "ambient_session")
        self.assertTrue(rebuilt.validation_result.passed)


if __name__ == "__main__":
    unittest.main()

