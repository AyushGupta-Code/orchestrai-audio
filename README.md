# orchestrai-audio

`orchestrai-audio` is a beginner-friendly Python repository for building a simple, agentic audio workflow engine in clear phases.

The project takes a freeform request, classifies it, builds a structured audio plan, routes it through a LangGraph workflow, generates placeholder or simple local artifacts, validates the results, and stores metadata in SQLite. The current implementation is still intentionally lightweight, but the repo is now organized so another developer can read it quickly and run it locally.

## Project Overview

The long-term goal is to support natural-language requests such as:

- "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
- "Turn this chapter into an audiobook with fitting background music"
- "Generate 2 hours of calm rain ambience for studying"
- "Create a guided focus session with intro prompts and break reminders"
- "Make a custom timeline with intro, work blocks, breaks, and outro"

The current system can already:

- parse a freeform request into a request type
- build a structured plan with segments
- route the plan through a LangGraph workflow
- choose stub or optional local backends
- generate placeholder artifacts, or simple local WAV files in limited cases
- validate the generated outputs
- retry once if validation fails
- save run metadata, plan JSON, backend routing, and validation results to SQLite
- optionally reuse local plan templates for richer defaults
- optionally cache repeated requests to avoid recomputing the same run

## Supported Request Types

- `music_session`
- `pomodoro_session`
- `audiobook`
- `ambient_session`
- `custom_timeline`

## Architecture Summary

The repository stays intentionally simple:

- `app/services/request_parser.py`: rule-based request parsing
- `app/services/planning_service.py`: structured planning layer
- `app/services/routing_service.py`: workflow path selection
- `app/services/backend_routing_service.py`: backend choice selection
- `app/services/music_service.py`: stub or simple local music/ambient artifact generation
- `app/services/voice_service.py`: stub or optional local voice generation
- `app/services/validation_service.py`: output checks and retry support
- `app/graph/workflow.py`: LangGraph orchestration
- `app/storage/run_repository.py`: SQLite persistence

High-level flow:

1. Parse request
2. Route to workflow path
3. Build structured plan
4. Route to backends
5. Generate segment artifacts
6. Stitch final output
7. Validate outputs
8. Retry once on failure
9. Save run metadata

## Folder Structure

```text
app/
  api/         Future FastAPI layer
  core/        Config and SQLite helpers
  graph/       LangGraph state, workflow, and routed subgraph helpers
  models/      Dataclass schemas for requests, plans, routing, and validation
  services/    Parser, planner, routing, generation, stitching, validation
  storage/     Artifact and SQLite repository helpers
data/
  artifacts/   Generated local artifacts
docs/
  ROADMAP.md   Phase checklist
  PHASE_LOG.md Implementation history by phase
scripts/
  run_demo.py  CLI demo entry point
tests/         Lightweight unittest coverage for core paths
templates/     Optional reusable plan templates
```

## Setup Instructions

### Default Setup

This is the recommended setup. It uses the safe stub fallback path.

```bash
conda create -n orchestrai-audio python=3.11
conda activate orchestrai-audio
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

### Optional Real Integrations

Phase 8 added a few optional local integrations. These are not required.

Optional packages:

```bash
python3 -m pip install pyttsx3
python3 -m pip install transformers
```

Optional environment flags:

```bash
export ORCH_AUDIO_ENABLE_REAL_REQUEST_UNDERSTANDING=1
export ORCH_AUDIO_REQUEST_SENTIMENT_MODEL=/path/to/local/model
export ORCH_AUDIO_ENABLE_REAL_VOICE=1
export ORCH_AUDIO_VOICE_BACKEND=pyttsx3
export ORCH_AUDIO_ENABLE_REAL_MUSIC=1
export ORCH_AUDIO_MUSIC_BACKEND=wave_tone
```

Fallback behavior:

- if optional dependencies are missing, the system stays on stub outputs
- if an optional real backend fails, the service falls back to the stub path
- the repo should remain runnable without extra packages

### Optional Advanced Features

Phase 10 adds a few small engineering extras that remain optional:

- Docker support for running the CLI demo in a container
- a small GitHub Actions workflow for tests and compile checks
- optional local template retrieval for reusable planning defaults
- optional local request-result caching

Template retrieval flag:

```bash
export ORCH_AUDIO_ENABLE_TEMPLATE_RETRIEVAL=1
```

Request cache flag:

```bash
export ORCH_AUDIO_ENABLE_REQUEST_CACHE=1
```

## CLI Run Examples

Run the demo script from the repository root:

```bash
python3 scripts/run_demo.py "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
python3 scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
python3 scripts/run_demo.py "Create a guided focus session with intro prompts and break reminders"
```

The demo prints:

- the structured plan summary as JSON
- the saved `run_id`
- the final artifact path
- the list of segment artifact paths

## Sample Requests

These are good demo inputs for the current repository:

- "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
- "Turn this chapter into an audiobook with fitting background music"
- "Generate 2 hours of calm rain ambience for studying"
- "Create a guided focus session with intro prompts and break reminders"
- "Make a custom timeline with intro, work blocks, breaks, and outro"

## Example Requests And Expected Output Shape

### Pomodoro Example

Request:

```text
Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro
```

Expected output characteristics:

- `request_type`: `pomodoro_session`
- repeated focus and break segments
- `break_pattern`: `25 minutes work / 5 minutes break`
- both music and voice backend routing
- final stitched artifact plus per-segment artifacts

### Audiobook Example

Request:

```text
Turn this chapter into an audiobook with fitting background music
```

Expected output characteristics:

- `request_type`: `audiobook`
- intro music, narration blocks, interlude, outro
- both voice and music backends selected
- validation metadata saved with the run

### Ambient Example

Request:

```text
Generate 2 hours of calm rain ambience for studying
```

Expected output characteristics:

- `request_type`: `ambient_session`
- long ambient segments
- no narration backend selected
- ambient placeholder files or simple WAV artifacts if enabled

### Guided Focus Example

Request:

```text
Create a guided focus session with intro prompts and break reminders
```

Expected output characteristics:

- `request_type`: `custom_timeline`
- intro, work, break, and outro style segments
- voice cues on guidance segments
- backend routing and validation metadata stored

## API Examples

The FastAPI service is still not implemented in the current repo state, but this is the shape the future API is expected to expose.

Planned health check:

```bash
curl http://127.0.0.1:8000/health
```

Planned generation request:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Generate 2 hours of calm rain ambience for studying"}'
```

Planned response shape:

```json
{
  "run_id": "run_123456789abc",
  "request_type": "ambient_session",
  "plan": {
    "title": "Ambient Session: Generate 2 hours of calm rain ambience...",
    "segments": []
  },
  "segment_artifacts": [],
  "final_artifact_path": "data/artifacts/run_123456789abc/final_mix.txt"
}
```

## Testing

Run the lightweight test suite:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Current tests cover:

- request parsing
- structured planning
- backend routing
- validation behavior
- template retrieval safety
- run-record cache serialization

## Docker

Build the image:

```bash
docker build -t orchestrai-audio .
```

Run the default demo:

```bash
docker run --rm orchestrai-audio
```

Run a custom request:

```bash
docker run --rm orchestrai-audio \
  python scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
```

## Docker Compose

Run the demo service:

```bash
docker compose up --build
```

The compose file mounts `./data` into the container so generated artifacts stay
on the host machine.

## GitHub Actions

A minimal workflow is included at [`.github/workflows/ci.yml`](/mnt/d/Projects/orchestrai-audio/.github/workflows/ci.yml).

It runs:

- dependency installation
- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m compileall app scripts tests`

## Optional Template Retrieval

Template retrieval is intentionally small and local. Template data lives in
[`templates/plan_templates.json`](/mnt/d/Projects/orchestrai-audio/templates/plan_templates.json).

When `ORCH_AUDIO_ENABLE_TEMPLATE_RETRIEVAL=1` is enabled, the planner can reuse
template hints such as:

- default style
- default mood
- default pacing
- reusable notes

If the feature is disabled or the template file is unavailable, planning
continues normally.

## Optional Request Cache

Request-result caching is also optional and file-based.

When `ORCH_AUDIO_ENABLE_REQUEST_CACHE=1` is enabled:

- a normalized request string is hashed
- the resulting `RunRecord` is stored under `data/cache/`
- repeated identical requests can return the cached result immediately

This keeps the cache easy to inspect and easy to delete without special tools.

## Notes On Current State

Implemented now:

- request parsing
- structured planning
- workflow routing
- backend routing
- validation and one retry
- SQLite metadata persistence
- optional real local integrations with stub fallbacks

Not implemented yet:

- FastAPI service
- full real model coverage
- advanced validation or quality scoring
- Docker, CI, MCP, or retrieval support

## Documentation

- Roadmap: [docs/ROADMAP.md](/mnt/d/Projects/orchestrai-audio/docs/ROADMAP.md)
- Phase log: [docs/PHASE_LOG.md](/mnt/d/Projects/orchestrai-audio/docs/PHASE_LOG.md)

## What Comes Next

Phase 10 optional work is now in place with Docker, CI, template retrieval,
and request caching. The repository is ready for any future advanced additions
that the project may still want, but it already works well as a small local
engineering demo.
