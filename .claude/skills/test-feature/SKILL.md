---
name: test-feature
description: Test a feature implementation by analyzing branch changes, running the project's automated checks, and verifying behavior. Trigger when the user wants to test, verify, or validate a feature, branch, or PR before review.
---

# Test Feature

Test a feature implementation by analyzing branch changes, understanding the requirements, running tariffa's automated checks, and verifying behavior.

This is tariffa: `apps/api` is a FastAPI backend (Pydantic AI, Postgres + pgvector, S3, Claude API) checked with `ruff` and `pytest` via `uv`. `apps/web` is a thin Next.js client checked with `pnpm`. There is no central task tracker — requirements come from a GitHub issue or a local `TODO.md`.

## Input

- `{{issue_or_description}}` — Either a GitHub issue number/URL OR a plain-text description of what to test.

## Prerequisites

- Working in a feature branch with changes
- For backend checks: `uv` available in `apps/api`
- For frontend checks: `pnpm` available; local dev server (`pnpm --filter web run dev`) running on `http://localhost:3000` if you need to exercise the UI

## Steps

### 1. Validate Input

If `{{issue_or_description}}` is empty, ask: "Give me a GitHub issue number/URL or describe the feature you want to test." Wait for a response. Otherwise proceed.

### 2. Determine Context Source

Identify whether the input is a GitHub issue reference or a description:

1. **If it looks like an issue** (e.g., `#42`, a number, or a `github.com/.../issues/N` URL):
   - Fetch it with `gh issue view <number>` and extract the title, body, and any acceptance criteria / checklist.
   - If it can't be found, fall back to treating the input as a plain description.
2. **If there's no issue but a local `TODO.md` exists**, check it for the matching item and use that as the requirements source.
3. **If it's a plain description**, use it directly.

Store the context:
- `task_name`: issue title or "Manual Test"
- `task_ref`: issue number or "N/A"
- `requirements`: the acceptance criteria / description to verify

### 3. Analyze Branch Changes

Understand what changed:

1. Current branch: `git branch --show-current`
2. If on `main`, warn: "You're on main. Switch to a feature branch to test specific changes."
3. Changed files: `git diff main...HEAD --name-only`
4. Stats: `git diff main...HEAD --stat`
5. Categorize the changes:
   - **Backend logic / agents:** `apps/api/**` — Pydantic AI agents, services, orchestration, RAG, compliance rules
   - **API routes:** FastAPI route handlers in `apps/api`
   - **Data models / persistence:** Pydantic schemas, SQLAlchemy models, migrations in `apps/api`
   - **Thin client:** `apps/web/**` — pages, components, upload UI, TanStack Query hooks
6. Document: list modified files, identify affected endpoints/pages, note what functionality changed.

### 4. Correlate Changes with Test Targets

Decide what to test based on the changes and requirements:

- **`apps/api` changes** → run the relevant `pytest` suites and exercise affected endpoints.
- **`apps/web` changes** → map files to routes (`apps/web/app/[path]/page.tsx` → `http://localhost:3000/[path]`) and plan a quick manual or browser pass over the affected pages.
- Define concrete scenarios tied to the requirements: for each, note the entry point (endpoint or URL), the actions, and the expected result.

### 5. Run Automated Checks

Run the project's checks for whatever the diff touched.

**Backend (`apps/api`):**

```bash
uv run ruff check apps/api
uv run pytest apps/api -q
```

Scope `pytest` to the affected paths (e.g. `uv run pytest apps/api/tests/test_<area>.py -q`) for a fast loop, then run the full suite before declaring done.

**Frontend (`apps/web`):**

```bash
pnpm --filter web run typecheck
pnpm --filter web run lint
```

Record pass/fail and capture any error output for the report.

### 6. Verify Behavior

For backend features, confirm the endpoint or pipeline stage produces the expected typed output for representative inputs (use the integration tests, or call the endpoint directly with a stubbed LLM/S3 where appropriate — don't hit the real Claude API or live S3).

For UI features, if a dev server is running, exercise the affected pages and confirm the expected flow (upload → review → prep-sheet draft) works and the console/network are clean. If no browser tooling is available, do a focused manual pass and note what you checked.

### 7. Evaluate Results

For each scenario, mark **PASS** (expected matched, no errors), **FAIL** (mismatch or errors), or **BLOCKED** (couldn't complete). Compile any failing checks, errors, or unexpected behavior. Assess overall readiness:
- All pass → ready for review
- Some fail → list specific issues to fix
- Critical failures → needs rework

### 8. Generate Test Report

Return a report in this shape:

```markdown
## Feature Test Results

**Task:** [task_ref] - [task_name]
**Branch:** [branch-name]
**Tested:** [date/time]

### Requirements
[Summary of what was supposed to be implemented]

### Changes Analyzed
| File | Change Type |
| ---- | ----------- |
| `apps/api/...` | Modified |
| `apps/web/...` | Added |

**Affected areas:** [list]

### Automated Checks
- `uv run ruff check apps/api` — [PASS/FAIL]
- `uv run pytest apps/api` — [PASS/FAIL] ([N passed, M failed])
- `pnpm --filter web run typecheck` — [PASS/FAIL]
- `pnpm --filter web run lint` — [PASS/FAIL]

### Scenarios
#### Scenario 1: [Description]
- **Entry point:** [endpoint or URL]
- **Actions:** [steps]
- **Expected:** [result]
- **Actual:** [result]
- **Status:** PASS / FAIL / BLOCKED

### Summary
| Metric | Count |
| ------ | ----- |
| Total  | X |
| Passed | Y |
| Failed | Z |
| Blocked | W |

**Overall:** READY FOR REVIEW / NEEDS FIXES / PARTIALLY WORKING

### Issues to Address
1. **Issue:** [description] — **Scenario:** [which] — **Expected/Actual:** [...] — **Suggested fix:** [if obvious]

### Next Steps
- [ ] Fix identified issues (if any)
- [ ] Re-run checks after fixes
- [ ] Open a PR for review
- [ ] Update the GitHub issue / `TODO.md`
```

### 9. Record Results (Optional)

If the requirements came from a GitHub issue, post the summary as a comment:

```bash
gh issue comment <number> --body "<test results summary>"
```

If you're tracking work in a local `TODO.md`, check off the item or note the outcome there instead.

## Output Summary

Return the report to the user and ask:
1. If all checks passed: "All checks passed. Want me to help open a PR?"
2. If some failed: "Some checks failed. Want me to investigate and fix the issues?"
3. If blocked: "Some checks couldn't be completed. Want me to help resolve the blockers?"
