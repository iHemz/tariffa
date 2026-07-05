---
name: test
description: Write and run tests for tariffa across the pyramid — unit, assembly/integration, and end-to-end — on both the FastAPI backend (pytest) and the Next.js frontend (Vitest + React Testing Library + Playwright).
argument-hint: "[path or feature to test, or 'setup' to scaffold the tooling]"
---

# Test — tariffa's testing methodology

The single source of truth for **how we test**. `/principal` (Phase 3) and `/ship` delegate here. Invoke directly to test a module or flow, or with `setup` to scaffold the tooling the first time.

Guiding rule: **a refactor or feature without tests is not done.** Tests pin behavior so we can change code fearlessly. See `.claude/rules/code-quality.md` and `.claude/rules/composable-design.md` — this skill is how those rules get exercised.

## The test pyramid

Write many fast unit tests, fewer integration tests, and a small number of end-to-end tests over the flows that actually matter.

| Layer | Backend (`apps/api`) | Frontend (`apps/web`) |
|---|---|---|
| **Unit** — one function/agent/component, no I/O | `pytest` (`asyncio_mode = "auto"` for async) | Vitest + React Testing Library |
| **Assembly/integration** — units wired together, boundaries faked | FastAPI `TestClient` against `src.main:app`; agents via pydantic-ai `TestModel`, repositories via stateful fakes | RTL rendering a view/component with `lib/api.ts` or the query hooks mocked |
| **End-to-end** — real user flow in a browser | — | Playwright driving the running app |

**What to fake, and what not to.** Never call the real Claude API, a real Postgres/pgvector instance, or real S3 in unit/integration tests — they cost money, are slow, and are non-deterministic. Instead:

- **Agents (LLM):** drive Pydantic AI agents with pydantic-ai's `TestModel` (or `FunctionModel` for a scripted reply) so they run with no API key and no network.
- **Persistence:** depend on a repository/port and pass a **stateful fake** (per `code-quality.md` — fakes over mocks), never the real DB session.
- **S3 / external boundaries:** `MagicMock` only at the deep boundary, kept out of test bodies.

E2E runs against the app but should point at a disposable test database, never production.

## Backend — pytest

**Toolchain:** `pytest` + `pytest-asyncio` (both already in `apps/api/pyproject.toml`, `asyncio_mode = "auto"`) and FastAPI's `TestClient`. Tests live in `apps/api/tests/`, mirroring `src/` (`tests/agents/`, `tests/routes/`, `tests/models/`). File names: `test_<module>.py`. Import from the `src` package: `from src.main import app`, `from src.agents.extraction import ...`.

**Run (from `apps/api`):**
```bash
cd apps/api && uv run pytest              # all
cd apps/api && uv run pytest -k <name>    # filter
cd apps/api && uv run pytest --cov=src    # coverage (needs pytest-cov, see setup)
```

**Patterns:**
- **Pure logic first.** Field normalization, classification scoring, which-regulators decisions, Form M assembly — extract these into pure functions and test them exhaustively (happy path + malformed input + edge cases). Cheapest, highest-value coverage.
- **Agents via `TestModel`.** Override the agent's model so the run is deterministic and offline; assert it's plumbed to the right typed output and that guards (media type, empty input) hold. Every agent-to-agent handoff is a validated Pydantic model — assert the type, not a raw dict.
- **Services with fakes.** A service depends on a repository and on agents; test it by injecting a stateful `FakeRepository` and a `TestModel`-backed agent. Assert on stored state (`fake.saved`), not on `assert_called_with`.
- **Routes via `TestClient`.** Instantiate `app`, override the FastAPI `Depends` that wires the service (so it receives fakes), and assert status codes, validation errors, and response shape.

**Unit example (pure function):**
```python
# apps/api/tests/agents/test_classification.py
from src.agents.classification import which_regulators
from src.models.classification import Regulator

def test_chemicals_route_to_nafdac_and_son():
    regulators = which_regulators("2811.22.00")
    assert Regulator.NAFDAC in regulators
    assert Regulator.SON in regulators
```

**Agent example (offline via `TestModel`):**
```python
# apps/api/tests/agents/test_extraction.py
from pydantic_ai.models.test import TestModel
from src.agents.extraction import extraction_agent
from src.models.extraction import ExtractedDocument

def test_extraction_returns_typed_document():
    with extraction_agent.override(model=TestModel()):
        result = extraction_agent.run_sync("invoice text")
    assert isinstance(result.output, ExtractedDocument)
```

**Assembly example (route via `TestClient`):**
```python
# apps/api/tests/routes/test_health.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_reports_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

## Frontend — Vitest + RTL + Playwright

**Unit/component:** Vitest + React Testing Library + `jsdom`. Test files are **colocated** next to source (`DocumentCard.test.tsx`, `api.test.ts`).

**E2E:** Playwright specs in `apps/web/e2e/`, named `*.spec.ts` (e.g. `upload-flow.spec.ts`).

**Run (tooling must be set up first — see below):**
```bash
pnpm --filter web test           # vitest, once
pnpm --filter web test:watch     # vitest, watch mode
pnpm --filter web test:e2e       # playwright
```

**Patterns:**
- **Test behavior, not implementation.** Query by role/text/label as a user would (`getByRole`, `getByText`), not by test IDs or class names, wherever practical.
- **Components in isolation.** Render a view or leaf component with the data layer mocked (`vi.mock('@/lib/api', ...)` or the TanStack Query hook it uses — import hooks directly per `.claude/rules/barrel-exports.md`). Assert what the user sees: loading, empty, error, and success states.
- **E2E over the paths that matter.** Cover the flows whose breakage hurts: upload invoice → review extraction → see compliance flags → Form M prep sheet. Keep the set small and stable.
- **Cover every UX state** the feature exposes — loading, empty, error, success — matching `/principal` Phase 4's user-first checklist and `.claude/rules/design-tokens.md`.

**Component example:**
```tsx
// apps/web/features/documents/DocumentCard.test.tsx
import { render, screen } from '@testing-library/react';
import { DocumentCard } from './DocumentCard';

it('shows the compliance status', () => {
  render(<DocumentCard doc={{ filename: 'invoice.pdf', status: 'flagged' } as any} />);
  expect(screen.getByText(/flagged/i)).toBeInTheDocument();
});
```

## First-time setup (`/test setup`)

Only when the tooling isn't present yet. Add it, wire the scripts, commit one green smoke test per layer to prove the harness works, then ship via `/ship`.

**Backend:** `pytest` + `pytest-asyncio` are already installed and `asyncio_mode = "auto"` is set. If you need coverage, add it:
```bash
cd apps/api && uv add --dev pytest-cov
```
Ensure `apps/api/tests/` mirrors `src/` and holds a `conftest.py` with the shared fixtures (stateful repository fakes, a `TestModel`-backed agent factory, any `Depends` overrides).

**Frontend:** no test tooling is installed yet. Add it:
```bash
pnpm --filter web add -D vitest @vitejs/plugin-react jsdom \
  @testing-library/react @testing-library/jest-dom @testing-library/user-event
pnpm --filter web add -D @playwright/test
```
Add `vitest.config.ts` (jsdom environment, `@` path alias, `setupFiles`), a `vitest.setup.ts` importing `@testing-library/jest-dom`, and `playwright.config.ts`. Add scripts to `apps/web/package.json`: `"test": "vitest run"`, `"test:watch": "vitest"`, `"test:e2e": "playwright test"`.

## Definition of done

- New/changed **backend logic** ships with pytest unit tests; new **routes** ship with a `TestClient` assembly test; each pipeline **agent** has at least one golden-case test (known input → expected typed output).
- New/changed **frontend components** ship with an RTL test covering their states; **new user-facing flows** get (or extend) a Playwright spec.
- The relevant gate is green before `/ship`: `cd apps/api && uv run pytest` and/or `pnpm --filter web test`.
- Every agent-to-agent handoff asserted as a validated Pydantic model — no raw dicts across a boundary.
- No test hits the real Claude API, a real/production database, or real S3.
