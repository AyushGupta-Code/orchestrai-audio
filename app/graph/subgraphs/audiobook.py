"""Audiobook-specific workflow helpers."""

from __future__ import annotations

from app.graph.state import WorkflowState
from app.services.planning_service import build_audiobook_plan
from app.services.run_service import generate_run_id, generate_segment_artifacts


def build_audiobook_plan_node(state: WorkflowState) -> WorkflowState:
    """Create the narration-and-music plan for an audiobook request."""
    plan = build_audiobook_plan(state["parsed_request"])
    plan.notes.append("Workflow path: audiobook.")
    return {
        "plan": plan,
        "run_id": generate_run_id(),
    }


def generate_audiobook_artifacts_node(state: WorkflowState) -> WorkflowState:
    """Generate placeholder artifacts for narration and support music."""
    return {
        "segment_artifacts": generate_segment_artifacts(
            state["run_id"],
            state["plan"],
            state["backend_routing"],
        ),
    }
