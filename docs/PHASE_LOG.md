# Phase Log

## Phase 0: Repo Scaffold And Documentation

### Phase Name

Phase 0: repo scaffold and documentation

### What Was Completed

- Created the initial folder structure for the application, docs, data, scripts, and tests.
- Added placeholder Python package files so the repository has a clear starting shape.
- Added a minimal `pyproject.toml` so the repo can be installed in editable mode.
- Added a minimal `requirements.txt` with no external packages yet because Phase 0 does not need them.
- Added a `.gitignore` for virtual environments, caches, and future local artifacts.
- Wrote the first version of the `README.md` with the project overview, future use cases, architecture direction, and phased implementation plan.
- Added a roadmap checklist and this phase log.
- Added a simple verification script for the scaffold.

### Files Created Or Modified

- `.gitignore`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/__init__.py`
- `app/api/__init__.py`
- `app/core/__init__.py`
- `app/graph/__init__.py`
- `app/models/__init__.py`
- `app/services/__init__.py`
- `app/storage/__init__.py`
- `scripts/phase0_check.py`
- `tests/__init__.py`
- `data/artifacts/.gitkeep`

### How To Inspect The Repo

1. Create and activate a virtual environment.
2. Install the project in editable mode:

```bash
python3 -m pip install -e .
```

3. Inspect the scaffold verification output:

```bash
python3 scripts/phase0_check.py
```

4. Review the project documentation:

```bash
sed -n '1,240p' README.md
sed -n '1,240p' docs/ROADMAP.md
sed -n '1,260p' docs/PHASE_LOG.md
```

5. Optionally list the starter structure:

```bash
find app docs scripts tests data -maxdepth 3 | sort
```

### Known Limitations

- No audio planning or generation logic exists yet.
- No API exists yet.
- No database schema exists yet.
- No artifact generation exists yet.
- No LangGraph workflow exists yet.
- No external model or audio dependencies are installed yet.

### What The Next Phase Will Build

Phase 1 will introduce a very small, deterministic stub pipeline that can:

- accept a freeform text request
- classify the request type at a basic level
- create a structured audio plan with segments
- write placeholder output artifacts and metadata locally

## Phase 1: Multipurpose Request Planning And Stub Pipeline

### Phase Name

Phase 1: multipurpose request planning and stub pipeline

### What Was Built

- Added a rule-based request parser that converts freeform text into one of five request types:
  `music_session`, `pomodoro_session`, `audiobook`, `ambient_session`, or `custom_timeline`.
- Added lightweight dataclass schemas for requests, segment plans, full plans, and run records.
- Added a deterministic planning service that builds timeline segments for each supported request type.
- Added placeholder artifact generation for music, narration, and ambient segments.
- Added a stub stitching step that creates a final placeholder artifact for the full run.
- Added SQLite persistence for run metadata and the full saved plan.
- Added a demo script that accepts a freeform request and prints the plan plus artifact paths.

### Files Created Or Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `requirements.txt`
- `app/core/config.py`
- `app/core/database.py`
- `app/models/schemas.py`
- `app/services/request_parser.py`
- `app/services/planning_service.py`
- `app/services/music_service.py`
- `app/services/voice_service.py`
- `app/services/stitching_service.py`
- `app/services/run_service.py`
- `app/storage/artifacts.py`
- `app/storage/run_repository.py`
- `scripts/run_demo.py`

### How To Run The Demo

1. Create and activate a virtual environment.
2. Install the project in editable mode:

```bash
python3 -m pip install -e .
```

3. Run the demo script with a freeform request:

```bash
python3 scripts/run_demo.py "Make 5 hours of Indian jazz music with a 5-minute break after every 25-minute pomodoro"
```

Additional examples:

```bash
python3 scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
python3 scripts/run_demo.py "Create a guided focus session with intro voice prompts and breaks"
```

4. Inspect generated files:

```bash
find data/artifacts -maxdepth 2 -type f | sort
```

5. Inspect the SQLite database if needed:

```bash
python3 - <<'PY'
import sqlite3
connection = sqlite3.connect("data/orchestrai_audio.db")
for row in connection.execute("SELECT run_id, request_type, title FROM runs ORDER BY created_at DESC"):
    print(row)
PY
```

### Current Limitations

- The parser is purely rule-based and only handles simple keyword matches.
- Plans are deterministic templates, not model-generated plans.
- Artifact files are text placeholders, not real audio files.
- Stitching is simulated by writing a text manifest for the final mix.
- There is no API yet.
- There is no validation or retry logic yet.

### What Phase 2 Will Do

Phase 2 will expose the stub pipeline through a simple FastAPI service, likely with endpoints for:

- health checks
- plan-only generation
- full run execution
- run lookup by `run_id`

## Phase 3: LangGraph Supervisor Workflow

### Phase Name

Phase 3: LangGraph supervisor workflow

### What Changed

- Replaced the direct sequential orchestration path with a small LangGraph workflow.
- Added a shared graph state object that carries request text, parsed request data, the generated plan, artifact paths, and the saved run record.
- Converted the major pipeline stages into graph nodes:
  - parse request
  - create plan
  - generate segment artifacts
  - stitch final output
  - save run metadata
- Kept the existing service logic in place so the graph only changes orchestration, not behavior.
- Added a thin workflow wrapper so callers can run the graph and receive the final saved `RunRecord`.

### Files Modified

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `requirements.txt`
- `pyproject.toml`
- `app/graph/state.py`
- `app/graph/workflow.py`
- `app/services/run_service.py`
- `scripts/run_demo.py`

### How The Graph Works

- The graph starts with a state dictionary containing `request_text`.
- `parse_request` normalizes the text into a structured request.
- `create_plan` builds the deterministic timeline plan and assigns a `run_id`.
- `generate_segment_artifacts` writes placeholder segment outputs to disk.
- `stitch_final_output` creates a final placeholder mix artifact.
- `save_run_metadata` persists the completed run to SQLite and returns the saved `RunRecord`.

The graph is intentionally linear so the execution flow is easy to read.

### How To Run It

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

2. Run the demo script:

```bash
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
```

The demo still prints the plan summary, run id, final artifact path, and segment artifact paths.

### Limitations

- The graph is linear and does not branch or use subgraphs yet.
- The parser and planner are still deterministic rule-based stubs.
- Artifacts are still text placeholders rather than real audio files.
- The FastAPI layer is still not implemented in this repository state.
- This environment did not have `pip`, so the LangGraph runtime could not be verified locally after adding the dependency.

### What Phase 4 Will Do

Phase 4 will add workflow routing and subgraphs so different request types can
follow specialized graph paths instead of sharing one linear sequence.

## Phase 4: Workflow Routing And Subgraphs

### Phase Name

Phase 4: workflow routing and subgraphs

### Completed Work

- Added a routing service that chooses a workflow path from the parsed request type.
- Updated the LangGraph workflow so it now branches after parsing instead of using one fully linear path.
- Added simple mode-specific workflow helper modules for:
  - `music_session`
  - `pomodoro_session`
  - `audiobook`
  - `ambient_session`
  - `custom_timeline`
- Kept the implementation deliberately explicit so each request type has a visible internal path.
- Reused the existing planning and artifact generation services rather than rewriting business logic.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/graph/state.py`
- `app/graph/workflow.py`
- `app/graph/subgraphs/__init__.py`
- `app/graph/subgraphs/music_session.py`
- `app/graph/subgraphs/pomodoro_session.py`
- `app/graph/subgraphs/audiobook.py`
- `app/graph/subgraphs/ambient_session.py`
- `app/graph/subgraphs/custom_timeline.py`
- `app/services/routing_service.py`

### Usage Notes

Install the dependencies and run the existing demo script:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
```

The user-facing behavior is still the same: the demo prints the structured plan,
the saved `run_id`, the final artifact path, and the segment artifact paths.

Internally, the request now follows a routed graph path based on `request_type`.

### Limitations

- The routed paths are still small deterministic stubs.
- The mode-specific subgraph modules are helper modules, not standalone compiled subgraphs.
- Artifact generation is still placeholder text output, not real audio generation.
- The FastAPI layer still does not exist in this repository state.
- This environment still could not verify the LangGraph runtime end to end because `langgraph` is not installed locally here.

### What Phase 5 Will Do

Phase 5 will add a more structured planning agent so the plan can be generated
from richer reasoning rather than only from fixed templates.

## Phase 5: Structured Planning Stage

### Phase Name

Phase 5: structured planning stage

### Completed Work

- Expanded the planning schema so the full plan now includes:
  - `mood`
  - `style`
  - `pacing`
  - `break_pattern`
  - `output_strategy`
- Expanded each segment plan so it now includes:
  - `mood`
  - `style`
  - richer downstream prompt fields
- Refactored the rule-based planner so it behaves more like a structured planning layer.
- Added simple heuristics for mood, style, and pacing inference.
- Integrated the richer structured plan into the existing routed LangGraph workflow.
- Preserved plan persistence in SQLite by continuing to save the full structured plan JSON in run metadata.
- Updated artifact generation so placeholder files now reflect the richer plan fields.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/models/schemas.py`
- `app/services/planning_service.py`
- `app/services/music_service.py`
- `app/services/voice_service.py`
- `app/services/stitching_service.py`
- `app/graph/workflow.py`

### Usage Notes

Run the existing demo script as before:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Make a custom timeline with intro, work blocks, breaks, and outro"
```

The output plan is now richer and more expressive. It still remains
deterministic, but it gives downstream generation stages better structured data.

### Limitations

- The planning layer is still heuristic and rule-based, not model-driven.
- It behaves like a simple planning agent, but there are not yet multiple agents.
- The FastAPI layer still does not exist in this repository state.
- Artifact files are still placeholder text files, not real generated audio.
- This environment still could not run the LangGraph workflow end to end because `langgraph` is not installed locally here.

### What Phase 6 Will Do

Phase 6 will add a backend routing layer so the system can choose different
generation backends for music, narration, ambience, or stitching needs.

## Phase 6: Backend Routing Stage

### Phase Name

Phase 6: backend routing stage

### Completed Work

- Added a structured backend routing object with:
  - `music_backend_name`
  - `voice_backend_name`
  - `stitching_strategy`
  - `routing_reason`
- Added a simple backend routing service that chooses stub backends from the structured plan.
- Integrated backend routing into the LangGraph workflow as a dedicated step after planning.
- Passed routing decisions into downstream artifact generation and stitching services.
- Saved routing decisions in run metadata alongside the structured plan.
- Updated the local SQLite schema helper so older databases gain the new `routing_json` column automatically.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/core/database.py`
- `app/models/schemas.py`
- `app/graph/state.py`
- `app/graph/workflow.py`
- `app/services/backend_routing_service.py`
- `app/services/music_service.py`
- `app/services/voice_service.py`
- `app/services/stitching_service.py`
- `app/services/run_service.py`
- `app/storage/run_repository.py`
- `app/graph/subgraphs/music_session.py`
- `app/graph/subgraphs/pomodoro_session.py`
- `app/graph/subgraphs/audiobook.py`
- `app/graph/subgraphs/ambient_session.py`
- `app/graph/subgraphs/custom_timeline.py`

### Usage Notes

Run the demo as before:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
```

The output behavior is still stubbed, but the run metadata and placeholder
artifact files now show which backends were selected and why.

### Limitations

- Backend routing is still fully rule-based.
- The selected backend names are placeholders, not real integrated providers.
- The FastAPI layer still does not exist in this repository state.
- Real backend capability checks and dynamic fallback logic do not exist yet.
- This environment still could not run the LangGraph workflow end to end because `langgraph` is not installed locally here.

### What Phase 7 Will Do

Phase 7 will add validation and retry logic so the system can detect weak
outputs and retry or recover in a simple, inspectable way.

## Phase 7: Validation And Retry Logic

### Phase Name

Phase 7: validation and retry logic

### Completed Work

- Added a structured validation result object to run metadata.
- Added a validation service that checks:
  - the plan contains at least one segment
  - segment artifact paths are present
  - expected segment artifact files exist
  - the final stitched artifact path is present
  - the final stitched artifact file exists
- Added retry state to the shared graph state with a small retry limit.
- Added a validation node and a retry decision node to the LangGraph workflow.
- If validation fails and retries remain, the graph now loops back into generation cleanly.
- Saved validation results in SQLite metadata alongside the plan and backend routing data.
- Added a lightweight database migration helper for the new `validation_json` column.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/models/schemas.py`
- `app/core/database.py`
- `app/graph/state.py`
- `app/graph/workflow.py`
- `app/storage/run_repository.py`
- `app/services/validation_service.py`

### Usage Notes

Run the demo as before:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
```

The pipeline now validates the generated outputs before saving the run. If a
validation check fails, the graph retries generation once and then saves the
final validation result in run metadata.

### Limitations

- Validation is intentionally shallow and only checks obvious completeness conditions.
- Retry behavior is limited to a single extra generation attempt.
- The FastAPI layer still does not exist in this repository state.
- Real quality scoring and semantic validation are not implemented yet.
- This environment still could not run the LangGraph workflow end to end because `langgraph` is not installed locally here.

### What Phase 8 Will Do

Phase 8 will begin integrating real generation backends so the orchestration
layers added so far can operate on actual audio generation providers.

## Phase 8: Real Model Integration

### Phase Name

Phase 8: real model integration

### Completed Work

- Added simple configuration flags for enabling or disabling optional real integrations.
- Added an optional request-understanding hook that can use a local `transformers` sentiment pipeline when configured.
- Added an optional local voice backend integration using `pyttsx3` when installed and enabled.
- Added a very small real local music and ambient backend that generates WAV tone files using only the Python standard library.
- Preserved stub fallbacks for all upgraded services so the repo still runs without optional dependencies.
- Updated backend routing so it can select real backend names when those integrations are enabled.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `requirements.txt`
- `app/core/config.py`
- `app/storage/artifacts.py`
- `app/services/request_parser.py`
- `app/services/planning_service.py`
- `app/services/backend_routing_service.py`
- `app/services/music_service.py`
- `app/services/voice_service.py`

### Usage Notes

The default runnable path is still the stub path:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
```

Optional real integrations can be enabled with environment flags, for example:

```bash
export ORCH_AUDIO_ENABLE_REAL_MUSIC=1
export ORCH_AUDIO_ENABLE_REAL_VOICE=1
export ORCH_AUDIO_VOICE_BACKEND=pyttsx3
python3 scripts/run_demo.py "Turn this chapter into an audiobook with fitting background music"
```

If a real integration is unavailable or fails, the service falls back to the
stub implementation automatically.

### Limitations

- The real music backend is intentionally simple and only generates synthetic WAV tones.
- The real voice backend depends on optional local `pyttsx3` support, which may not be available on every machine.
- The request-understanding model hook only works when `transformers` is installed and a local model path is configured.
- This environment does not currently have `pyttsx3`, `transformers`, or `langgraph` installed, so only static verification was possible here.

### What Phase 9 Will Do

Phase 9 will focus on polish, examples, and making the repository easier to run
and demonstrate with cleaner documentation and usage flows.

## Phase 9: Polish And Examples

### Phase Name

Phase 9: polish and examples

### Completed Work

- Rewrote the `README.md` so it is easier to scan on GitHub and easier for another developer to run.
- Added clearer sections for:
  - project overview
  - supported request types
  - architecture summary
  - folder structure
  - setup instructions
  - CLI examples
  - planned API examples
  - sample requests
  - expected output shapes
  - testing
- Added lightweight unit tests for the core stable paths:
  - request parsing
  - structured planning
  - backend routing
  - validation
- Kept the tests dependency-light by using the Python standard library `unittest` module.

### Files Changed

- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `tests/test_request_parser.py`
- `tests/test_planning_service.py`
- `tests/test_backend_routing_service.py`
- `tests/test_validation_service.py`

### Usage Notes

Default setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Run the CLI demo:

```bash
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
```

Run the tests:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Limitations

- The README now documents planned API examples, but the FastAPI layer itself is still not implemented.
- The lightweight tests cover core logic paths, not full graph execution.
- This environment still does not have `langgraph`, so only static verification and unit tests that avoid graph runtime dependencies are practical here.

### What Phase 10 Will Do

Phase 10 is reserved for optional advanced additions such as MCP support,
Docker, CI automation, or retrieval-related features.

## Phase 10: Optional Engineering Features

### Phase Name

Phase 10: optional engineering features

### Completed Work

- Added a minimal [`Dockerfile`](/mnt/d/Projects/orchestrai-audio/Dockerfile) for running the CLI demo in a container.
- Added a minimal [`docker-compose.yml`](/mnt/d/Projects/orchestrai-audio/docker-compose.yml) for local containerized demo runs.
- Added a small GitHub Actions workflow at [`.github/workflows/ci.yml`](/mnt/d/Projects/orchestrai-audio/.github/workflows/ci.yml) that installs dependencies, runs unit tests, and compiles Python files.
- Added optional local template retrieval using [`templates/plan_templates.json`](/mnt/d/Projects/orchestrai-audio/templates/plan_templates.json).
- Added optional file-based request-result caching under `data/cache/`.
- Added lightweight tests for template retrieval safety and cache-related serialization behavior.

### Files Changed

- `.gitignore`
- `README.md`
- `docs/ROADMAP.md`
- `docs/PHASE_LOG.md`
- `app/core/config.py`
- `app/models/schemas.py`
- `app/services/planning_service.py`
- `app/services/run_service.py`
- `app/services/template_retrieval_service.py`
- `app/services/cache_service.py`
- `templates/plan_templates.json`
- `data/cache/.gitkeep`
- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `tests/test_template_retrieval_service.py`
- `tests/test_cache_service.py`

### Usage Notes

Default local run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
python3 scripts/run_demo.py "Generate 2 hours of calm rain ambience for studying"
```

Enable template retrieval:

```bash
export ORCH_AUDIO_ENABLE_TEMPLATE_RETRIEVAL=1
```

Enable request caching:

```bash
export ORCH_AUDIO_ENABLE_REQUEST_CACHE=1
```

Run the test suite:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Build and run with Docker:

```bash
docker build -t orchestrai-audio .
docker run --rm orchestrai-audio
```

### Limitations

- MCP was intentionally not added because the repository still does not expose a stable API or tool boundary where it would be clearly useful.
- Template retrieval is local-file-based and intentionally simple.
- Request caching is local-file-based and not meant for distributed usage.
- The Docker workflow is focused on the CLI demo, not a production service.

### Phase 10 Outcome

The optional advanced phase is complete. The repository now includes a small
set of useful modern engineering features without making the local workflow
harder to understand or run.
