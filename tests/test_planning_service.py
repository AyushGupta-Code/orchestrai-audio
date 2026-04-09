"""Lightweight tests for the structured planning layer."""

from __future__ import annotations

import unittest

from app.services.planning_service import build_audio_plan
from app.services.request_parser import parse_request


class PlanningServiceTests(unittest.TestCase):
    """Verify that plans carry the expected structured fields."""

    def test_pomodoro_plan_contains_break_pattern_and_segments(self) -> None:
        request = parse_request(
            "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
        )
        plan = build_audio_plan(request)

        self.assertEqual(plan.request_type, "pomodoro_session")
        self.assertTrue(plan.needs_breaks)
        self.assertEqual(plan.break_pattern, "25 minutes work / 5 minutes break")
        self.assertGreater(len(plan.segments), 1)

    def test_audiobook_plan_contains_structured_fields(self) -> None:
        request = parse_request("Turn this chapter into an audiobook with fitting background music")
        plan = build_audio_plan(request)

        self.assertEqual(plan.request_type, "audiobook")
        self.assertTrue(plan.needs_narration)
        self.assertEqual(plan.output_strategy, "narration_with_supporting_music_segments")
        self.assertTrue(all(segment.mood for segment in plan.segments))
        self.assertTrue(all(segment.style for segment in plan.segments))

    def test_ambient_plan_uses_long_form_strategy(self) -> None:
        request = parse_request("Generate 2 hours of calm rain ambience for studying")
        plan = build_audio_plan(request)

        self.assertEqual(plan.request_type, "ambient_session")
        self.assertEqual(plan.output_strategy, "long_form_ambient_layers")
        self.assertFalse(plan.needs_narration)


if __name__ == "__main__":
    unittest.main()

