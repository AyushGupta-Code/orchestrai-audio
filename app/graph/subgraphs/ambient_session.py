"""Ambient-session-specific workflow helpers."""

from __future__ import annotations

from app.graph.state import WorkflowState
from app.services.planning_service import build_ambient_plan
from app.services.run_service import generate_run_id, generate_segment_artifacts


def build_ambient_plan_node(state: WorkflowState) -> WorkflowState:
    """Create the ambience-oriented plan for an ambient request."""
    plan = build_ambient_plan(state["parsed_request"])
    plan.notes.append("Workflow path: ambient_session.")
    return {
        "plan": plan,
        "run_id": generate_run_id(),
    }


def generate_ambient_artifacts_node(state: WorkflowState) -> WorkflowState:
    """Generate placeholder artifacts for ambience segments."""
    return {
        "segment_artifacts": generate_segment_artifacts(
            state["run_id"],
            state["plan"],
            state["backend_routing"],
        ),
    }
