"""Custom-timeline-specific workflow helpers."""

from __future__ import annotations

from app.graph.state import WorkflowState
from app.services.planning_service import build_custom_timeline_plan
from app.services.run_service import generate_run_id, generate_segment_artifacts


def build_custom_timeline_plan_node(state: WorkflowState) -> WorkflowState:
    """Create the generic multi-part plan for a custom timeline request."""
    plan = build_custom_timeline_plan(state["parsed_request"])
    plan.notes.append("Workflow path: custom_timeline.")
    return {
        "plan": plan,
        "run_id": generate_run_id(),
    }


def generate_custom_timeline_artifacts_node(state: WorkflowState) -> WorkflowState:
    """Generate placeholder artifacts for the custom timeline segments."""
    return {
        "segment_artifacts": generate_segment_artifacts(
            state["run_id"],
            state["plan"],
            state["backend_routing"],
        ),
    }
