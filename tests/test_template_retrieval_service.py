"""Tests for optional template retrieval helpers."""

from __future__ import annotations

import unittest

from app.services.template_retrieval_service import load_template_for_request_type


class TemplateRetrievalTests(unittest.TestCase):
    """Verify template retrieval stays safe when disabled."""

    def test_returns_dict_even_when_feature_is_disabled(self) -> None:
        template = load_template_for_request_type("ambient_session")
        self.assertIsInstance(template, dict)


if __name__ == "__main__":
    unittest.main()

