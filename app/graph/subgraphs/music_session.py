"""Music-session-specific workflow helpers."""

from __future__ import annotations

from app.graph.state import WorkflowState
from app.services.planning_service import build_music_plan
from app.services.run_service import generate_run_id, generate_segment_artifacts


def build_music_plan_node(state: WorkflowState) -> WorkflowState:
    """Create the music-oriented plan for a music session request."""
    plan = build_music_plan(state["parsed_request"])
    plan.notes.append("Workflow path: music_session.")
    return {
        "plan": plan,
        "run_id": generate_run_id(),
    }


def generate_music_artifacts_node(state: WorkflowState) -> WorkflowState:
    """Generate placeholder artifacts for music-session segments."""
    return {
        "segment_artifacts": generate_segment_artifacts(
            state["run_id"],
            state["plan"],
            state["backend_routing"],
        ),
    }
