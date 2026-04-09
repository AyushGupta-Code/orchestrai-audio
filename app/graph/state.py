"""Shared state definition for the Phase 3 LangGraph workflow.

The graph passes one dictionary-shaped state object from node to node.
Each node reads the fields it needs and returns only the updates it produces.
This keeps the workflow easy to trace because the data flow is explicit.
"""

from __future__ import annotations

from typing import TypedDict

from app.models.schemas import (
    AudioRequest,
    AudioRequestPlan,
    BackendRoutingDecision,
    RunRecord,
    ValidationResult,
)


class WorkflowState(TypedDict, total=False):
    """State shared by the LangGraph supervisor workflow."""

    request_text: str
    parsed_request: AudioRequest
    parsed_request_type: str
    workflow_path: str
    plan: AudioRequestPlan
    backend_routing: BackendRoutingDecision
    validation_result: ValidationResult
    segment_artifacts: list[str]
    final_artifact: str
    run_id: str
    run_record: RunRecord
    retry_count: int
    max_retries: int
    errors: list[str]
