"""Pomodoro-session-specific workflow helpers."""

from __future__ import annotations

from app.graph.state import WorkflowState
from app.services.planning_service import build_pomodoro_plan
from app.services.run_service import generate_run_id, generate_segment_artifacts


def build_pomodoro_plan_node(state: WorkflowState) -> WorkflowState:
    """Create the work-and-break plan for a pomodoro request."""
    plan = build_pomodoro_plan(state["parsed_request"])
    plan.notes.append("Workflow path: pomodoro_session.")
    return {
        "plan": plan,
        "run_id": generate_run_id(),
    }


def generate_pomodoro_artifacts_node(state: WorkflowState) -> WorkflowState:
    """Generate placeholder artifacts for focus and break segments."""
    return {
        "segment_artifacts": generate_segment_artifacts(
            state["run_id"],
            state["plan"],
            state["backend_routing"],
        ),
    }
