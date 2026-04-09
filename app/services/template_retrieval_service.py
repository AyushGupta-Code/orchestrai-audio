"""Optional retrieval helpers for reusable plan templates.

This is intentionally small. Templates live in one local JSON file and can
provide default planning hints such as style, pacing, or reusable notes.
"""

from __future__ import annotations

import json

from app.core.config import ENABLE_TEMPLATE_RETRIEVAL, TEMPLATE_LIBRARY_PATH
from app.models.schemas import AudioRequestPlan


def enrich_plan_with_template(plan: AudioRequestPlan) -> AudioRequestPlan:
    """Optionally enrich a plan with a reusable local template.

    If template retrieval is disabled or the template file is missing, the plan
    is returned unchanged. This keeps the advanced feature optional.
    """
    template = load_template_for_request_type(plan.request_type)
    if not template:
        return plan

    if plan.style == "hybrid" and template.get("default_style"):
        plan.style = str(template["default_style"])
    if plan.mood == "balanced" and template.get("default_mood"):
        plan.mood = str(template["default_mood"])
    if plan.pacing == "moderate" and template.get("default_pacing"):
        plan.pacing = str(template["default_pacing"])
    if template.get("default_output_strategy") and plan.output_strategy == "single_stub_mix":
        plan.output_strategy = str(template["default_output_strategy"])

    template_notes = [str(note) for note in template.get("notes", [])]
    if template_notes:
        plan.notes.extend(template_notes)

    return plan


def load_template_for_request_type(request_type: str) -> dict[str, object]:
    """Load one template block from the local template library."""
    if not ENABLE_TEMPLATE_RETRIEVAL:
        return {}

    if not TEMPLATE_LIBRARY_PATH.exists():
        return {}

    try:
        payload = json.loads(TEMPLATE_LIBRARY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    templates = payload.get("request_type_templates", {})
    selected_template = templates.get(request_type, {})
    if not isinstance(selected_template, dict):
        return {}
    return selected_template
