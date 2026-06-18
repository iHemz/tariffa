---
name: taskgen
description: Generate a structured XML task list from a PRD (and optional design notes). Tasks are organized into waves by layer (tests first, then apps/api, then the thin apps/web client) with complexity ratings for model selection.
argument-hint: "[prd-path] [optional-design-notes-path]"

---

# TaskGen: Generate Task List from PRD

Convert a PRD (and optional design notes) into a structured XML task list. Tasks are organized into waves by layer order with complexity ratings that drive model selection.

This is tariffa: an AI agent pipeline (Pydantic AI) that extracts data from invoices/packing lists, classifies goods against HS codes and regulators (NAFDAC, SON), flags compliance issues, and drafts a Form M prep sheet. `apps/api` (FastAPI) owns all logic — agent orchestration, Postgres + pgvector, S3, Claude API. `apps/web` (Next.js) is a thin client with no business logic. Generated tasks must respect that split.

**Input:** $ARGUMENTS — Path to PRD file, optionally followed by a design-notes path

**Usage:**
- `/taskgen docs/prds/feature-name.md` — Generate from PRD only
- `/taskgen docs/prds/feature-name.md docs/prds/design-feature-name.md` — Generate from PRD + design notes

## Steps

### 1. Parse Documents

Read the PRD at the first path in $ARGUMENTS. If a second path is provided, read the design notes.

Extract:
- **From PRD:** Functional requirements, technical approach, affected parts of the pipeline, implementation phases, acceptance criteria
- **From design notes (if provided):** Implementation sequence, file list, integration points, any UI layout or data-flow details for `apps/web`

### 2. Load Architecture Context

Read these for pattern awareness before decomposing:
- `CLAUDE.md` — repo navigation and non-negotiables
- `docs/02-architecture.md` — service boundaries (why Next.js + FastAPI + Pydantic AI)
- `docs/03-agent-pipeline.md` — the four agents and their typed handoffs
- `docs/04-data-models.md` — the Pydantic schemas that are the contracts between pipeline stages

Relevant patterns also live in `references/patterns/{logging,validation}.md` and `references/new-agent-architecture/`.

### 3. Decompose into Tasks

Break requirements into implementation tasks. **Wave 0 is test-first** — it produces failing tests that encode the public contracts (Pydantic models between pipeline stages, FastAPI route request/response shapes, agent inputs/outputs). Waves 1..N implement against those tests until they go green.

**Wave 0 — Test-first (always first when contracts are well defined):**

- Extract every public contract from the PRD/design notes: Pydantic models crossing a pipeline boundary, FastAPI routes with request/response shapes, agent input/output types, pure helper functions.
- For each contract, create a failing test task:
  - **Unit tests** (complexity 2) — one task per pure function / Pydantic model / agent contract. Use `pytest` with real fakes over heavy mocking; see `references/patterns/validation.md`.
  - **Integration tests** (complexity 3) — one task per FastAPI route. Call the route via FastAPI's `TestClient` / `httpx.AsyncClient` against the app, stubbing the LLM call and S3 where needed. Don't hit the real Claude API or live S3 in tests.
- Tests MUST assert against the public contract (Pydantic shapes, API shapes, agent I/O) — NOT internal helpers. Brittle tests that lock down implementation details defeat the purpose.
- Tests MUST execute (`uv run pytest [path]`) and be RED at the end of Wave 0. A test that doesn't run is not a test.

**Waves 1..N — Implementation (in layer order):**

1. **Data models** (complexity 1-2): Pydantic schemas, enums, typed contracts between pipeline stages (`apps/api`)
2. **Persistence** (complexity 2-3): SQLAlchemy/asyncpg models, Postgres + pgvector queries, migrations, S3 access (`apps/api`)
3. **Agents & services** (complexity 3-4): Pydantic AI agents, orchestration, RAG retrieval, compliance logic, business rules (`apps/api`)
4. **API layer** (complexity 2-3): FastAPI route handlers, request/response models, presigned-URL endpoints, background tasks (`apps/api`)
5. **Thin client** (complexity 2-4): Next.js pages/components, upload UI (react-dropzone → presigned S3), review screen, TanStack Query hooks, Tailwind v4 styling (`apps/web`)

Keep the split honest: validation, AI orchestration, and all LLM/DB/S3 calls live in `apps/api`. `apps/web` only renders state and calls the API — it never talks to Postgres, S3, or the Claude API directly, and large file uploads go browser → S3 via a presigned URL.

Each implementation wave's gate: types + lint pass and the `pytest` (or web typecheck) green-count strictly increases vs the previous wave. The final implementation wave must leave all Wave 0 tests green.

**When design notes specify UI details:**
- `apps/web` tasks (`.tsx` files) should include the specific layout/component references from the notes — which page, which component, what data it renders from the API.
- Style with Tailwind v4 utilities; avoid vague "style appropriately" — cite the intended layout from the design notes.

For each task, specify:
- **id**: Hierarchical identifier (e.g., `0.1`, `1.1`, `2.1`)
- **complexity**: 1-5 rating (drives model selection)
- **file**: Target file path
- **action**: `create` or `modify`
- **description**: What to implement (specific, not vague). For Wave 0 test tasks: name the contract being asserted and the test location.
- **verify**: Verification command. Wave 0 tasks: `uv run pytest [path] -q` (expected RED). Waves 1..N: `uv run ruff check [path] && uv run pytest [path] -q` for `apps/api`, or `pnpm --filter web run typecheck && pnpm --filter web run lint` for `apps/web`.

### 4. Build Waves

Group tasks into waves based on file conflicts and dependencies:
- **Wave 0 is the test-first wave** — all test tasks run in parallel, different test files
- Tasks in the same wave can run in parallel (different files)
- Tasks that depend on earlier tasks go in later waves
- Wave ordering: Wave 0 (tests) → layer order (Data models → Persistence → Agents & services → API → thin client)

### 5. Add Mandatory Final Tasks

Every task list MUST include a final wave with code review and full validation: `uv run ruff check . && uv run pytest` for `apps/api`, `pnpm --filter web run typecheck && pnpm --filter web run lint` for `apps/web`.

### 6. Generate XML Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<execution_plan feature="[feature-name]" prd="[prd-path]" generated="[ISO-date]">
  <wave number="0" description="Test-first: failing tests encoding public contracts">
    <task id="0.1" complexity="2" status="pending"
          file="apps/api/tests/test_[agent].py" action="create">
      <description>
        Write failing unit tests for the [agent/model]: assert [specific contract — Pydantic shape / agent I/O].
        Use pytest with real fakes per references/patterns/validation.md. Tests must run and FAIL.
      </description>
      <verify>uv run pytest apps/api/tests/test_[agent].py -q</verify>
    </task>
    <task id="0.2" complexity="3" status="pending"
          file="apps/api/tests/test_[route].py" action="create">
      <description>
        Write failing integration test for POST /[route]: call via TestClient, stub the LLM + S3,
        assert request schema and response shape from the PRD contract.
      </description>
      <verify>uv run pytest apps/api/tests/test_[route].py -q</verify>
    </task>
  </wave>
  <wave number="1" description="Data models: Pydantic schemas and types">
    <task id="1.1" complexity="2" status="pending"
          file="apps/api/[module]/models.py" action="create">
      <description>Define Pydantic schemas for [entity]; makes Wave 0 unit tests typecheck.</description>
      <verify>uv run ruff check apps/api/[module]/models.py</verify>
    </task>
  </wave>
  <!-- More waves; final wave must leave all Wave 0 tests green... -->
</execution_plan>
```

### 7. Save Task File

Save to: `docs/prds/tasks-[feature-slug].xml` (same directory as the PRD).

### 8. Output Summary

```
## Task List Generated

**File:** `docs/prds/tasks-[feature-slug].xml`
**Total Tasks:** [count]
**Waves:** [count]

**Next Step:**
Work the waves in order — Wave 0 tests first (RED), then implement each layer until green.
```

## Complexity Calibration

| Rating | Description | Model |
|--------|-------------|-------|
| 1 | Simple type export, config file, enum | haiku |
| 2 | Pydantic schema, basic component, simple query | haiku |
| 3 | Agent/service method, FastAPI route, RAG retrieval step | sonnet |
| 4 | Multi-file integration, complex compliance logic, pipeline wiring | opus |
| 5 | System-wide change, new agent in the pipeline, architecture migration | opus |
