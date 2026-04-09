"""Simple data models for the stub pipeline.

The models use dataclasses so they stay lightweight and easy to serialize.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class AudioRequest:
    """A normalized representation of the freeform user request."""

    text: str
    request_type: str
    title: str
    total_duration_minutes: int

    def to_dict(self) -> dict[str, object]:
        """Convert the dataclass into a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AudioRequest":
        """Rebuild an `AudioRequest` from saved JSON-compatible data."""
        return cls(
            text=str(payload["text"]),
            request_type=str(payload["request_type"]),
            title=str(payload["title"]),
            total_duration_minutes=int(payload["total_duration_minutes"]),
        )


@dataclass
class SegmentPlan:
    """A single planned timeline segment.

    Every segment can describe music, narration, ambience, or a simple control
    block such as a pomodoro work or break segment.
    """

    segment_id: str
    name: str
    segment_type: str
    duration_minutes: int
    purpose: str
    mood: str
    style: str
    music_prompt: str | None = None
    narration_text: str | None = None
    ambient_prompt: str | None = None
    include_voice_cue: bool = False

    def to_dict(self) -> dict[str, object]:
        """Convert the dataclass into a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "SegmentPlan":
        """Rebuild a `SegmentPlan` from saved JSON-compatible data."""
        return cls(
            segment_id=str(payload["segment_id"]),
            name=str(payload["name"]),
            segment_type=str(payload["segment_type"]),
            duration_minutes=int(payload["duration_minutes"]),
            purpose=str(payload["purpose"]),
            mood=str(payload["mood"]),
            style=str(payload["style"]),
            music_prompt=payload.get("music_prompt"),
            narration_text=payload.get("narration_text"),
            ambient_prompt=payload.get("ambient_prompt"),
            include_voice_cue=bool(payload.get("include_voice_cue", False)),
        )


@dataclass
class AudioRequestPlan:
    """The full structured plan created from the parsed request."""

    request_type: str
    title: str
    total_duration_minutes: int
    mood: str
    style: str
    pacing: str
    needs_music: bool
    needs_narration: bool
    needs_breaks: bool
    break_pattern: str | None = None
    output_strategy: str = "single_stub_mix"
    segments: list[SegmentPlan] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convert the plan and nested segments into a plain dictionary."""
        payload = asdict(self)
        payload["segments"] = [segment.to_dict() for segment in self.segments]
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AudioRequestPlan":
        """Rebuild an `AudioRequestPlan` from saved JSON-compatible data."""
        return cls(
            request_type=str(payload["request_type"]),
            title=str(payload["title"]),
            total_duration_minutes=int(payload["total_duration_minutes"]),
            mood=str(payload["mood"]),
            style=str(payload["style"]),
            pacing=str(payload["pacing"]),
            needs_music=bool(payload["needs_music"]),
            needs_narration=bool(payload["needs_narration"]),
            needs_breaks=bool(payload["needs_breaks"]),
            break_pattern=payload.get("break_pattern"),
            output_strategy=str(payload.get("output_strategy", "single_stub_mix")),
            segments=[
                SegmentPlan.from_dict(segment_payload)
                for segment_payload in payload.get("segments", [])
            ],
            notes=[str(note) for note in payload.get("notes", [])],
        )


@dataclass
class BackendRoutingDecision:
    """Routing decision for which stub backends should handle the run.

    Phase 6 keeps this deliberately simple. The object records the selected
    backend names and the reason those choices were made so the decision is
    easy to inspect in saved metadata.
    """

    music_backend_name: str | None
    voice_backend_name: str | None
    stitching_strategy: str
    routing_reason: str

    def to_dict(self) -> dict[str, object]:
        """Convert the routing decision into a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BackendRoutingDecision":
        """Rebuild a backend routing decision from saved data."""
        return cls(
            music_backend_name=payload.get("music_backend_name"),
            voice_backend_name=payload.get("voice_backend_name"),
            stitching_strategy=str(payload["stitching_strategy"]),
            routing_reason=str(payload["routing_reason"]),
        )


@dataclass
class ValidationResult:
    """Validation summary for one pipeline run."""

    passed: bool
    checks: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    retry_count: int = 0

    def to_dict(self) -> dict[str, object]:
        """Convert the validation result into a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ValidationResult":
        """Rebuild a validation result from saved data."""
        return cls(
            passed=bool(payload["passed"]),
            checks=[str(check) for check in payload.get("checks", [])],
            failures=[str(failure) for failure in payload.get("failures", [])],
            retry_count=int(payload.get("retry_count", 0)),
        )


@dataclass
class RunRecord:
    """The persisted summary of one pipeline execution."""

    run_id: str
    created_at: str
    request_text: str
    request_type: str
    title: str
    total_duration_minutes: int
    plan: AudioRequestPlan
    backend_routing: BackendRoutingDecision
    validation_result: ValidationResult
    segment_artifacts: list[str]
    final_artifact_path: str

    def to_dict(self) -> dict[str, object]:
        """Convert the run record and nested plan into a plain dictionary."""
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "request_text": self.request_text,
            "request_type": self.request_type,
            "title": self.title,
            "total_duration_minutes": self.total_duration_minutes,
            "plan": self.plan.to_dict(),
            "backend_routing": self.backend_routing.to_dict(),
            "validation_result": self.validation_result.to_dict(),
            "segment_artifacts": list(self.segment_artifacts),
            "final_artifact_path": self.final_artifact_path,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "RunRecord":
        """Rebuild a saved run record from cached JSON-compatible data."""
        return cls(
            run_id=str(payload["run_id"]),
            created_at=str(payload["created_at"]),
            request_text=str(payload["request_text"]),
            request_type=str(payload["request_type"]),
            title=str(payload["title"]),
            total_duration_minutes=int(payload["total_duration_minutes"]),
            plan=AudioRequestPlan.from_dict(payload["plan"]),
            backend_routing=BackendRoutingDecision.from_dict(payload["backend_routing"]),
            validation_result=ValidationResult.from_dict(payload["validation_result"]),
            segment_artifacts=[str(path) for path in payload.get("segment_artifacts", [])],
            final_artifact_path=str(payload["final_artifact_path"]),
        )
