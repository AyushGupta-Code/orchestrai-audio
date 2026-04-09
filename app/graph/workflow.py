"""LangGraph workflow with routing, planning, backend routing, and validation.

Phase 6 keeps the explicit request routing and structured planning layers, then
adds one more simple decision step that chooses placeholder backend names and a
stitching strategy before generation begins.
"""

from __future__ import annotations

from datetime import UTC, datetime

from langgraph.graph import END, START, StateGraph

from app.core.database import initialize_database
from app.graph.state import WorkflowState
from app.graph.subgraphs.ambient_session import (
    build_ambient_plan_node,
    generate_ambient_artifacts_node,
)
from app.graph.subgraphs.audiobook import (
    build_audiobook_plan_node,
    generate_audiobook_artifacts_node,
)
from app.graph.subgraphs.custom_timeline import (
    build_custom_timeline_plan_node,
    generate_custom_timeline_artifacts_node,
)
from app.graph.subgraphs.music_session import (
    build_music_plan_node,
    generate_music_artifacts_node,
)
from app.graph.subgraphs.pomodoro_session import (
    build_pomodoro_plan_node,
    generate_pomodoro_artifacts_node,
)
from app.models.schemas import RunRecord, ValidationResult
from app.services.backend_routing_service import choose_backends
from app.services.request_parser import parse_request
from app.services.routing_service import choose_workflow_path
from app.services.stitching_service import create_final_artifact
from app.services.validation_service import validate_outputs
from app.storage.run_repository import save_run_record


def parse_request_node(state: WorkflowState) -> WorkflowState:
    """Parse freeform text into a normalized request."""
    parsed_request = parse_request(state["request_text"])
    return {
        "parsed_request": parsed_request,
        "parsed_request_type": parsed_request.request_type,
    }


def route_request_node(state: WorkflowState) -> WorkflowState:
    """Choose the internal workflow path for the parsed request."""
    workflow_path = choose_workflow_path(state["parsed_request"])
    return {"workflow_path": workflow_path}


def choose_plan_branch(state: WorkflowState) -> str:
    """Tell LangGraph which mode-specific planning node to run next."""
    path_to_node = {
        "music_session": "build_music_plan",
        "pomodoro_session": "build_pomodoro_plan",
        "audiobook": "build_audiobook_plan",
        "ambient_session": "build_ambient_plan",
        "custom_timeline": "build_custom_timeline_plan",
    }
    return path_to_node.get(state["workflow_path"], "build_custom_timeline_plan")


def route_backends_node(state: WorkflowState) -> WorkflowState:
    """Choose backend names and a stitching strategy from the structured plan."""
    return {"backend_routing": choose_backends(state["plan"])}


def choose_artifact_branch(state: WorkflowState) -> str:
    """Return to the correct mode-specific generation node after backend routing."""
    path_to_node = {
        "music_session": "generate_music_artifacts",
        "pomodoro_session": "generate_pomodoro_artifacts",
        "audiobook": "generate_audiobook_artifacts",
        "ambient_session": "generate_ambient_artifacts",
        "custom_timeline": "generate_custom_timeline_artifacts",
    }
    return path_to_node.get(state["workflow_path"], "generate_custom_timeline_artifacts")


def stitch_final_output_node(state: WorkflowState) -> WorkflowState:
    """Simulate a final stitched artifact from the generated segments."""
    final_artifact = create_final_artifact(
        state["run_id"],
        state["plan"],
        state["backend_routing"],
        state["segment_artifacts"],
    )
    return {"final_artifact": final_artifact}


def validate_outputs_node(state: WorkflowState) -> WorkflowState:
    """Validate the current generation attempt before saving metadata."""
    validation_result = validate_outputs(
        state["plan"],
        state["segment_artifacts"],
        state["final_artifact"],
        state["retry_count"],
    )
    return {"validation_result": validation_result}


def decide_retry_branch(state: WorkflowState) -> str:
    """Choose whether to save, or retry generation once more."""
    validation_result = state["validation_result"]
    if validation_result.passed:
        return "save_run_metadata"

    if state["retry_count"] < state["max_retries"]:
        return "increment_retry"

    return "save_run_metadata"


def increment_retry_node(state: WorkflowState) -> WorkflowState:
    """Increase the retry counter and record why another attempt will run."""
    next_retry_count = state["retry_count"] + 1
    updated_errors = list(state.get("errors", []))
    validation_result = state["validation_result"]
    updated_errors.append(
        f"Validation failed on attempt {state['retry_count'] + 1}: "
        + "; ".join(validation_result.failures)
    )
    return {
        "retry_count": next_retry_count,
        "errors": updated_errors,
    }


def save_run_metadata_node(state: WorkflowState) -> WorkflowState:
    """Persist the completed run into SQLite and return the saved record."""
    parsed_request = state["parsed_request"]
    plan = state["plan"]

    run_record = RunRecord(
        run_id=state["run_id"],
        created_at=datetime.now(UTC).isoformat(),
        request_text=parsed_request.text,
        request_type=plan.request_type,
        title=plan.title,
        total_duration_minutes=plan.total_duration_minutes,
        plan=plan,
        backend_routing=state["backend_routing"],
        validation_result=state.get(
            "validation_result",
            ValidationResult(
                passed=False,
                checks=[],
                failures=["Validation did not run."],
                retry_count=state.get("retry_count", 0),
            ),
        ),
        segment_artifacts=state["segment_artifacts"],
        final_artifact_path=state["final_artifact"],
    )
    save_run_record(run_record)
    return {"run_record": run_record}


def build_workflow():
    """Create and compile the Phase 4 routed workflow.

    The graph is intentionally explicit:
    parse -> route request -> mode-specific plan -> route backends
    -> mode-specific artifacts -> stitch -> validate -> retry or save
    """
    graph = StateGraph(WorkflowState)
    graph.add_node("parse_request", parse_request_node)
    graph.add_node("route_request", route_request_node)
    graph.add_node("build_music_plan", build_music_plan_node)
    graph.add_node("generate_music_artifacts", generate_music_artifacts_node)
    graph.add_node("build_pomodoro_plan", build_pomodoro_plan_node)
    graph.add_node("generate_pomodoro_artifacts", generate_pomodoro_artifacts_node)
    graph.add_node("build_audiobook_plan", build_audiobook_plan_node)
    graph.add_node("generate_audiobook_artifacts", generate_audiobook_artifacts_node)
    graph.add_node("build_ambient_plan", build_ambient_plan_node)
    graph.add_node("generate_ambient_artifacts", generate_ambient_artifacts_node)
    graph.add_node("build_custom_timeline_plan", build_custom_timeline_plan_node)
    graph.add_node("generate_custom_timeline_artifacts", generate_custom_timeline_artifacts_node)
    graph.add_node("route_backends", route_backends_node)
    graph.add_node("stitch_final_output", stitch_final_output_node)
    graph.add_node("validate_outputs", validate_outputs_node)
    graph.add_node("increment_retry", increment_retry_node)
    graph.add_node("save_run_metadata", save_run_metadata_node)

    graph.add_edge(START, "parse_request")
    graph.add_edge("parse_request", "route_request")
    graph.add_conditional_edges(
        "route_request",
        choose_plan_branch,
        {
            "build_music_plan": "build_music_plan",
            "build_pomodoro_plan": "build_pomodoro_plan",
            "build_audiobook_plan": "build_audiobook_plan",
            "build_ambient_plan": "build_ambient_plan",
            "build_custom_timeline_plan": "build_custom_timeline_plan",
        },
    )
    graph.add_edge("build_music_plan", "route_backends")
    graph.add_edge("build_pomodoro_plan", "route_backends")
    graph.add_edge("build_audiobook_plan", "route_backends")
    graph.add_edge("build_ambient_plan", "route_backends")
    graph.add_edge("build_custom_timeline_plan", "route_backends")
    graph.add_conditional_edges(
        "route_backends",
        choose_artifact_branch,
        {
            "generate_music_artifacts": "generate_music_artifacts",
            "generate_pomodoro_artifacts": "generate_pomodoro_artifacts",
            "generate_audiobook_artifacts": "generate_audiobook_artifacts",
            "generate_ambient_artifacts": "generate_ambient_artifacts",
            "generate_custom_timeline_artifacts": "generate_custom_timeline_artifacts",
        },
    )
    graph.add_edge("generate_music_artifacts", "stitch_final_output")
    graph.add_edge("generate_pomodoro_artifacts", "stitch_final_output")
    graph.add_edge("generate_audiobook_artifacts", "stitch_final_output")
    graph.add_edge("generate_ambient_artifacts", "stitch_final_output")
    graph.add_edge("generate_custom_timeline_artifacts", "stitch_final_output")
    graph.add_edge("stitch_final_output", "validate_outputs")
    graph.add_conditional_edges(
        "validate_outputs",
        decide_retry_branch,
        {
            "increment_retry": "increment_retry",
            "save_run_metadata": "save_run_metadata",
        },
    )
    graph.add_conditional_edges(
        "increment_retry",
        choose_artifact_branch,
        {
            "generate_music_artifacts": "generate_music_artifacts",
            "generate_pomodoro_artifacts": "generate_pomodoro_artifacts",
            "generate_audiobook_artifacts": "generate_audiobook_artifacts",
            "generate_ambient_artifacts": "generate_ambient_artifacts",
            "generate_custom_timeline_artifacts": "generate_custom_timeline_artifacts",
        },
    )
    graph.add_edge("save_run_metadata", END)

    return graph.compile()


def run_workflow(request_text: str) -> WorkflowState:
    """Run the compiled graph with a thin wrapper for callers.

    This wrapper keeps API and script integration simple. A caller only needs to
    provide the request text and read the final `run_record` from the result.
    """
    initialize_database()
    app = build_workflow()
    initial_state: WorkflowState = {
        "request_text": request_text,
        "retry_count": 0,
        "max_retries": 1,
        "errors": [],
    }
    return app.invoke(initial_state)
