# Production Quality Gate — Verify Before Every PR

**CONTEXT:** I'm a solo founder. There's no separate QA team and no second reviewer — the gate is me plus whatever the tooling and the agents catch. So the checks below are not bureaucracy; they're the only safety net between a change and a clearing agent relying on a wrong compliance flag. Treat a green gate as the bar for "done".

This applies to all changes — mine and any AI agent's.

---

## Pre-PR Checklist (Mandatory)

Before declaring an implementation complete or opening a PR, verify every item that applies. A PR opened without these is considered incomplete.

### 1. Build & Static Analysis

Frontend (`apps/web`):
- [ ] `pnpm --filter web run typecheck` passes with **zero errors**
- [ ] `pnpm --filter web run lint` passes with **zero errors**

Backend (`apps/api`):
- [ ] `ruff check apps/api` passes with **zero errors**
- [ ] `ruff format apps/api` leaves no changes (code is already formatted)

General:
- [ ] No `// @ts-ignore` / `# type: ignore` / lint-disable added without an inline reason comment
- [ ] The pre-commit hook runs clean (don't bypass with `--no-verify`)

### 2. Tests

- [ ] Backend logic has `pytest` cases and `pytest` (run from `apps/api`) is green
- [ ] Every new pure function has direct input/output tests
- [ ] Every new service method has tests using **fakes with real state** (per `.claude/rules/code-quality.md`) — not mocks of internal code
- [ ] Pipeline agents have at least one eval/golden-case test (known document → expected typed output)
- [ ] Test names state the **invariant being enforced**, not the behavior observed (e.g. `"flags an invoice with no HS code"`, not `"returns an error"`)
- [ ] No skipped tests added without justification in the PR description

### 3. Edge Cases Enumerated

For every change, explicitly think through and handle:
- [ ] `None` / empty inputs (empty arrays, empty strings, missing invoice fields)
- [ ] Malformed or partial uploads (scanned image with no text, wrong document type)
- [ ] Claude API / Pydantic AI failures (timeout, 429, 5xx, output that fails Pydantic validation) — caught and surfaced, not silently swallowed
- [ ] RAG retrieval returning nothing — the compliance agent must not invent a rule
- [ ] DB failures (connection drop, write conflict) — caught and surfaced
- [ ] Background-task failures — the user sees a clear failed state, not a stuck "running" row

### 4. Typed Contracts

- [ ] Every agent-to-agent handoff is a validated Pydantic model — no raw dicts crossing a pipeline boundary
- [ ] API request/response bodies are Pydantic models with `response_model` set
- [ ] Frontend payload types match the backend models

### 5. Grounding (Compliance Agent)

- [ ] Every compliance flag cites the retrieved regulatory text it came from
- [ ] No reliance on the model's unverified knowledge of Nigerian customs law
- [ ] The tool never claims to submit to NICIS / Trade Window — output is a draft only

### 6. Concern Isolation

- [ ] Independent side effects (notifications, analytics, background emits) wrapped in their **own** try/except — never block the main flow
- [ ] A successful DB write returns to the caller even if a downstream side effect fails (logged, not raised)
- [ ] No silent excepts — every except logs enough context to debug

### 7. Boundaries & Security

- [ ] Frontend stays a thin client — no business logic, no direct DB/S3/Claude calls
- [ ] All logic, validation, and AI orchestration live in `apps/api`
- [ ] No secrets, API keys, or PII logged
- [ ] User input validated through Pydantic at the route boundary before reaching services
- [ ] Large uploads use the presigned-URL flow (browser → S3), not proxied through both apps

### 8. Code Review

- [ ] Run `/code-review` on the diff before opening the PR
- [ ] Address every critical/high finding; note any deferred medium/low in the PR description

### 9. UI Changes

- [ ] If you can't verify the change in a real browser, **say so explicitly** in the PR — never claim UI works because types compile
- [ ] Cross-device interactions verified (per `.claude/rules/cross-device-interactions.md`)
- [ ] Token usage verified — no hardcoded colors/spacing (per `.claude/rules/design-tokens.md`)

### 10. PR Description

Every PR includes:
- [ ] **Summary** — what changed and why (the value, not the mechanics)
- [ ] **Test Plan** — explicit checklist of what was tested, including edge cases considered
- [ ] **Risk assessment** — what could break, and the rollback plan

A PR with an empty or generic test plan is incomplete.

---

## When in Doubt

Err toward **more testing, more explicit verification**. The cost of a slow PR is hours; the cost of a wrong compliance flag is a clearing agent's trust and a delayed shipment at the port. If a change feels risky and you can't fully verify it, **say so in the PR description** — a flagged risk I explicitly accept is fine; a silent one that breaks is not.
