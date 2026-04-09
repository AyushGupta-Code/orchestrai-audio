"""Lightweight tests for the request parser.

These tests focus on the stable, rule-based behavior we expect in the current
repository state. They avoid the optional real-integration paths so they remain
portable and fast.
"""

from __future__ import annotations

import unittest

from app.services.request_parser import parse_request


class RequestParserTests(unittest.TestCase):
    """Verify that freeform requests map to the expected request types."""

    def test_parses_pomodoro_request(self) -> None:
        request = parse_request(
            "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
        )
        self.assertEqual(request.request_type, "pomodoro_session")
        self.assertEqual(request.total_duration_minutes, 300)

    def test_parses_audiobook_request(self) -> None:
        request = parse_request("Turn this chapter into an audiobook with fitting background music")
        self.assertEqual(request.request_type, "audiobook")

    def test_parses_ambient_request(self) -> None:
        request = parse_request("Generate 2 hours of calm rain ambience for studying")
        self.assertEqual(request.request_type, "ambient_session")
        self.assertEqual(request.total_duration_minutes, 120)

    def test_parses_custom_timeline_request(self) -> None:
        request = parse_request("Create a guided focus session with intro prompts and break reminders")
        self.assertEqual(request.request_type, "custom_timeline")


if __name__ == "__main__":
    unittest.main()

