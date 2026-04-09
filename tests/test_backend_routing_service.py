"""Lightweight tests for backend routing decisions."""

from __future__ import annotations

import unittest

from app.services.backend_routing_service import choose_backends
from app.services.planning_service import build_audio_plan
from app.services.request_parser import parse_request


class BackendRoutingTests(unittest.TestCase):
    """Verify that structured plans lead to sensible backend choices."""

    def test_audiobook_chooses_voice_and_music_backends(self) -> None:
        plan = build_audio_plan(parse_request("Turn this chapter into an audiobook with fitting background music"))
        routing = choose_backends(plan)

        self.assertIsNotNone(routing.music_backend_name)
        self.assertIsNotNone(routing.voice_backend_name)
        self.assertIn("Audiobook requests need both narration", routing.routing_reason)

    def test_ambient_skips_voice_backend(self) -> None:
        plan = build_audio_plan(parse_request("Generate 2 hours of calm rain ambience for studying"))
        routing = choose_backends(plan)

        self.assertIsNotNone(routing.music_backend_name)
        self.assertIsNone(routing.voice_backend_name)
        self.assertEqual(routing.stitching_strategy, "ambient_layered_stitch")


if __name__ == "__main__":
    unittest.main()

