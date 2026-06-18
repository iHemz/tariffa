---
name: find-bug
description: Find Bug Workflow

---

# Find Bug Workflow

Systematic bug investigation workflow that triages, investigates, and proposes fixes across tariffa's stack (`apps/web` Next.js thin client; `apps/api` FastAPI + Pydantic AI + Postgres).

## Input

- `{{bug_description}}` - Description of the bug or unexpected behavior
- `{{urls}}` - (Optional) URLs to navigate to for client-side bugs

## Phase 1: Triage

**AI Task:** Determine the bug classification before investigation.

### 1.1 Validate Input

1. **If `{{bug_description}}` is empty:**
   - Ask: "Please describe the bug or unexpected behavior you're seeing"
   - Wait for response before proceeding

### 1.2 Classify Bug Type

Based on the bug description, classify as one of:

| Type            | Indicators                                                                                                                            | Investigation Path |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| **Client-Side** | UI rendering issues, component behavior, state management, visual glitches, browser console errors, user interaction problems         | → Phase 2A         |
| **Server-Side** | API errors (4xx/5xx), data not persisting, background task failures, agent/LLM failures, database inconsistencies, wrong API responses | → Phase 2B         |
| **Full-Stack**  | Data shows correctly in DB but wrong in UI, API returns correct data but UI misrenders, data correct in UI but wrong in DB            | → Phase 2A + 2B    |

### 1.3 Confirm Classification

**AI Task:** State your classification and reasoning:

```
Bug Classification: [Client-Side | Server-Side | Full-Stack]

Reasoning:
- [Key indicator 1 from description]
- [Key indicator 2 from description]

Investigation Path: Phase 2[A|B]
```

If uncertain, ask the user:

- "Does this bug involve the UI/browser behavior, or is it about data/API/agent processing?"

---

## Phase 2A: Client-Side Investigation

**Prerequisites:**

- Local dev server running (`pnpm --filter web run dev`)
- A browser automation tool available (e.g. `agent-browser`)
- URLs provided or identifiable from bug description

### 2A.1 Gather URLs

1. **If `{{urls}}` provided:** Parse into array (split by comma, trim whitespace)
2. **If `{{urls}}` empty:** Ask: "Please provide the URL(s) to investigate (comma-separated if multiple)"

### 2A.2 Navigate and Capture State

**AI Task:** For each URL:

1. **Navigate** and wait for the page to fully load (use incremental waits with snapshots).

2. **Capture evidence:**
   - Accessibility/snapshot tree for element structure
   - Console messages — errors/warnings
   - Network requests — failed or unusual API calls (to `apps/api`)
   - Screenshot — if visual context needed

3. **Document observations:**
   - Data displayed on page
   - Console errors (with stack traces)
   - Failed network requests (status codes, payloads)
   - Visual anomalies

### 2A.3 Reproduce the Bug

**AI Task:** If the bug requires interaction:

1. Snapshot to identify interactive elements
2. Perform the actions that trigger the bug
3. Capture state after each action
4. Document the exact reproduction steps

### 2A.4 Identify the Discrepancy

**AI Task:** Compare observed vs expected:

1. **Extract key data points:** IDs, names, values displayed; state indicators; data relationships
2. **Cross-reference (if multiple URLs):** compare data across pages, look for inconsistencies
3. **Document:** expected behavior, actual behavior, specific wrong values

---

## Phase 2B: Server-Side Investigation

**Prerequisites:**

- Local API running (`uv run fastapi dev` or the project's run command)
- A way to query Postgres (psql, a DB client, or an MCP tool)
- Terminal access for log observation

### 2B.1 Gather Context

**AI Task:** Collect information needed for investigation:

1. **If API endpoint involved:**
   - Ask: "What API endpoint is affected? (e.g., `/api/shipments`, `POST /api/uploads`)"
   - Ask: "What request payload triggers the bug?" (if applicable)

2. **If a background task or agent is involved:**
   - Ask: "Which pipeline stage or background task is failing?" (extraction / classification / compliance / Form M draft)
   - Ask: "What input triggers the failure?"

3. **If data inconsistency:**
   - Ask: "What entity/table is affected?" (e.g., shipments, documents, line_items)
   - Ask: "What specific row ID(s) show the problem?"

### 2B.2 Check Server Logs

**AI Task:** Examine terminal output for errors:

1. **Read the API dev server output** — look for recent errors, stack traces, warnings. Note any correlation/request IDs.

2. **Look for these patterns:**
   - `Traceback` / `Exception` - Runtime errors
   - `ValidationError` - Pydantic validation failures
   - `asyncpg.` / `sqlalchemy.exc.` - Database issues
   - `401/403` - Auth failures
   - `404` - Resource not found
   - `500` - Unhandled server errors
   - Anthropic/Claude API errors, rate limits, or truncated/refused completions in an agent stage

3. **Document findings:** error message and stack trace, timestamp, any correlation ID for tracing.

### 2B.3 Trace the API Route

**AI Task:** Follow the request through the stack:

1. **Find the API route:** locate the FastAPI router/handler for the endpoint in `apps/api`.

2. **Identify the dependency chain:**

   ```
   auth dependency → request validation (Pydantic) → handler → service
   ```

   - Check what Pydantic model validates the request
   - Check what auth dependency guards the route
   - Identify which service / agent method is called

3. **Trace to the service / agent layer:**
   - Find the service or Pydantic AI agent that handles the operation
   - Read the specific method being called
   - Note any repository calls, S3 calls, or Claude API calls

4. **Trace to the repository (if applicable):**
   - Find the repository (asyncpg/SQLAlchemy) implementation
   - Check the query being executed — filters, joins, projections

### 2B.4 Query Database State

**AI Task:** Verify data state in Postgres:

1. **Identify the table** (e.g., `Shipment` model → `shipments` table).
2. **Query relevant rows** matching the criteria.
3. **Verify data integrity:** does the row exist? Are required columns populated? Are foreign keys valid? Is the data in the expected state?
4. **Check related rows:** follow foreign-key references, verify parent/child relationships, check for orphaned references. For RAG issues, verify the relevant `pgvector` embeddings exist and are non-null.

### 2B.5 Investigate Background Tasks / Agents (if applicable)

**AI Task:** For pipeline or background-task failures:

1. **Find the task/agent:** locate the FastAPI background task or the Pydantic AI agent definition in `apps/api`.
2. **Check idempotency:** is the task safe to retry? Does it handle duplicate triggers?
3. **Trace the stages:** identify each step, check what each does, look for inter-stage dependencies. Confirm each stage hands off a **validated Pydantic model**, not a raw dict.
4. **Check the input payload:** is required data present? Are IDs/references valid? For an agent stage, is the prompt grounded in retrieved regulatory text (RAG) rather than relying on model memory?

### 2B.6 Identify the Server-Side Discrepancy

**AI Task:** Summarize findings:

1. **Data state analysis:** what is stored? what should be stored? what does the API return?
2. **Request flow analysis:** where in the stack does the bug manifest? what transformation causes it? what condition triggers it?
3. **Document:** expected server behavior, actual server behavior, specific values/state that are wrong.

### 2B.7 Common Server-Side Bug Patterns

| Pattern              | What to Look For                                        |
| -------------------- | ------------------------------------------------------- |
| Missing auth check   | Route missing the auth dependency                       |
| Validation bypass    | Pydantic model doesn't match expected input             |
| Raw dict across boundary | A pipeline stage passing/receiving an unvalidated dict instead of a Pydantic model |
| Ungrounded compliance | Compliance agent answering from model memory, not retrieved regulatory text |
| Race condition       | Read-then-write instead of an atomic update             |
| N+1 query            | Loop with individual DB calls instead of a batch        |
| Unhandled exception  | Missing try/except or error propagation                 |
| Stale reference      | Using an old ID after a row was updated/deleted          |
| Missing await        | Async coroutine not awaited                             |
| Transaction missing  | Multi-row update without a transaction                  |

---

## Phase 3: Code Tracing

**AI Task:** Trace from symptom to source based on bug type.

### 3.1 Identify Affected Components

**For Client-Side bugs:**

1. Search: "Where is the component that renders [page path]?"
2. Find the page component in `apps/web/app/`
3. Identify child components involved
4. Find hooks and state management (TanStack Query)

**For Server-Side bugs:**

1. Find the FastAPI route in `apps/api`
2. Search: "Where is the service/agent that handles [operation]?"
3. Find the service / Pydantic AI agent
4. Find the repository (asyncpg/SQLAlchemy)
5. Check background tasks / pipeline stages

### 3.2 Trace Data Flow

**Client-Side Flow:**

```
TanStack Query hook
    ↓
API response (fetch to apps/api)
    ↓
Component state / props
    ↓
Rendered output
```

**Server-Side Flow:**

```
FastAPI route (apps/api)
    ↓
auth dependency → Pydantic request validation
    ↓
Service / Pydantic AI agent
    ↓
Repository (asyncpg / SQLAlchemy)
    ↓
Postgres (+ pgvector)
```

**Pipeline Flow (agents):**

```
Trigger (upload complete / API call)
    ↓
Extraction agent → ExtractedInvoice (Pydantic)
    ↓
Classification agent → ClassifiedItems (Pydantic)
    ↓
Compliance agent (RAG-grounded) → ComplianceFindings (Pydantic)
    ↓
Form M draft → FormMPrepSheet (Pydantic)
    ↓
Persisted to Postgres
```

- Use Grep to find specific values/IDs/function names
- Look for transformation points where data could be corrupted (especially stage handoffs)

### 3.3 Check Common Bug Patterns

**Client-Side Patterns:**

| Pattern             | What to Look For                          |
| ------------------- | ----------------------------------------- |
| Stale closure       | Missing deps in `useEffect`/`useCallback` |
| Race condition      | Async operations without proper guards    |
| Incorrect reference | Wrong ID/key being used                   |
| State mutation      | Direct mutation instead of new state      |
| Missing null check  | Accessing properties on undefined         |
| Caching issue       | Stale TanStack Query data                 |
| Prop drilling error | Wrong prop passed through layers          |

**Server-Side Patterns:**

| Pattern                 | What to Look For                                     |
| ----------------------- | --------------------------------------------------- |
| Auth bypass             | Missing auth dependency on a protected route        |
| Validation gap          | Pydantic model doesn't cover an edge case           |
| Raw dict across boundary| Stage handoff not a validated Pydantic model        |
| Ungrounded compliance   | Agent not using retrieved regulatory text (RAG)     |
| Read-then-write race    | Should use an atomic UPDATE / `RETURNING`           |
| Missing await           | Unhandled coroutine in an async function            |
| N+1 query               | Loop with individual DB calls                       |
| Transaction missing     | Multi-row update needs atomicity                    |
| Error swallowing        | Except block without proper handling                |
| Stale service reference | Calling an old/renamed method                       |

---

## Phase 4: Root Cause Analysis

**AI Task:** Determine the definitive cause.

### 4.1 Identify Root Cause

Answer these questions:

1. **What exact line(s) cause the issue?** File path and line numbers, the problematic code snippet.
2. **Why does this produce incorrect behavior?** The logical flaw or missing handling, the conditions that trigger it.
3. **When does this occur?** Always, or under specific conditions? What state/data triggers it?

### 4.2 Assess Brittleness

1. **Severity:** how bad is the impact?
2. **Fragility:** is this code prone to similar bugs?
3. **Related patterns:** are there similar patterns elsewhere at risk?

### 4.3 Determine Scope

1. **Affected features:** what else might be impacted?
2. **Regression check:** was this caused by a recent change?

### 4.4 PRD Assessment

**AI Task:** Determine if a PRD is needed before proceeding to fix.

**A PRD is needed when:**

| Indicator                        | Explanation                                                |
| -------------------------------- | ---------------------------------------------------------- |
| **Architectural change**         | Fix requires refactoring multiple services or data flow    |
| **New feature disguised as bug** | "Bug" is actually missing functionality                    |
| **Multiple modules affected**    | Fix touches several modules or pipeline stages             |
| **Data model changes**           | New columns, schema changes, or migrations required        |
| **Design decisions needed**      | Multiple valid solutions with significant trade-offs       |
| **User-facing behavior change**  | Fix changes expected UX or introduces new patterns         |
| **Pipeline / contract scope**    | Agent contracts, API contracts, or stage handoffs affected |
| **Estimate > 4 hours**           | Complexity suggests formal planning                        |

**AI Task:** If ANY indicators apply, ask the user:

> "Based on the root cause analysis, this appears to require [specific indicator]. Would you like me to create a PRD before implementing the fix?"
>
> Options:
>
> 1. Yes, create a PRD (→ Phase 4B)
> 2. No, proceed with fix (→ Phase 5)

---

## Phase 4B: Create Bug-Triggered PRD

**Prerequisites:** Phase 4 complete, user opted for PRD creation

### 4B.1 Gather PRD Context

**AI Task:** Collect additional context from bug findings:

1. **From investigation:** root cause summary, affected modules/layers, data flow insights, related code patterns.
2. **Ask user (if not evident):**
   - "What is the expected behavior once fixed?"
   - "Are there related improvements we should bundle?"
   - "Who are the primary users affected?"

### 4B.2 Generate PRD

**AI Task:** Create a PRD using the bug findings as input.

**File naming:** `docs/prds/[feature-slug].md` (slug from the fix description, e.g. `shipment-sync-race-condition.md`).

**PRD Template (Bug-Triggered):**

````markdown
# PRD: [Fix Title - Derived from Bug]

**Status:** Draft | **Priority:** [From severity]
**Author:** AI-Generated | **Date:** [Today]
**Type:** Bug Fix / Refactor
**Triggered By:** Bug Investigation

---

## Executive Summary

[2-3 sentences: What bug was discovered, why it matters, what the fix entails]

## Problem Statement

### Original Bug Report

- **Description:** [From {{bug_description}}]
- **Reproduction Steps:** [From Phase 2]
- **Observed Behavior:** [From investigation]
- **Expected Behavior:** [Corrected state]

### Root Cause Analysis

- **Location:** `[file:line]` (from Phase 4)
- **Layer:** [Route | Dependency | Service | Agent | Repository | Schema]
- **Problem:** [Why it breaks - from Phase 4]
- **Code:**

  ```python
  # Problematic code from investigation
  ```

### Why a PRD?

[Explain which indicators triggered PRD creation]

## Target Users

| Persona     | Impact                     |
| ----------- | -------------------------- |
| [User type] | [How the bug affects them] |

## Goals & Success Metrics

- **Primary Goal:** [What "fixed" looks like]
- **Success Metrics:**
  - [ ] [Measurable outcome 1]
  - [ ] [Measurable outcome 2]

## Scope

### In Scope (MVP)

- [ ] [Core fix requirement 1]
- [ ] [Core fix requirement 2]

### Out of Scope

- [ ] [Related but deferred improvement]

## Technical Approach

### Affected Areas

| Area           | Changes            | Impact         |
| -------------- | ------------------ | -------------- |
| [From Phase 3] | [Required changes] | [High/Med/Low] |

### Architecture & Patterns

**Key Principles:**

- All business logic and AI orchestration live in `apps/api`
- Every pipeline handoff is a validated Pydantic model
- Compliance logic is RAG-grounded
- [Other relevant principles]

### Data Flow

[Diagram if helpful - copy from Phase 3 trace]

### Database Changes

**Schema Updates:** [If any]
**Migrations Required:** [Yes/No]

### API / Pipeline Changes

**Modified Endpoints:** [If any]
**Modified Stage Contracts:** [If any]

## Implementation Phases

### Phase 1: [First deliverable]

- [ ] [Task 1]
- [ ] [Task 2]

**Validation:** [How to verify]

### Phase 2: [Second deliverable]

- [ ] [Task 1]
- [ ] [Task 2]

**Validation:** [How to verify]

## Dependencies & Risks

| Risk                      | Impact   | Likelihood   | Mitigation   |
| ------------------------- | -------- | ------------ | ------------ |
| [Risk from investigation] | [Impact] | [Likelihood] | [Mitigation] |

## Acceptance Criteria

### Functional Criteria

- [ ] Bug no longer reproducible
- [ ] [Additional criteria]

### Quality Criteria

- [ ] `ruff check` passes (`apps/api`)
- [ ] `pytest` passes (`apps/api`)
- [ ] `pnpm --filter web run typecheck` / `lint` pass (if `apps/web` touched)
- [ ] Pipeline handoffs remain validated Pydantic models
- [ ] Background tasks/agents remain idempotent (if applicable)

---

_Generated from bug investigation on [date]_
````

### 4B.3 Save and Confirm

**AI Task:**

1. Create the `docs/prds/` folder if it doesn't exist
2. Save the PRD file
3. Confirm with user:

> "PRD created at `docs/prds/[slug].md`"
>
> Would you like me to:
>
> 1. Review and refine the PRD
> 2. Proceed to implement Phase 1

---

## Phase 5: Propose Fix

**AI Task:** Design a robust solution.

### 5.1 Immediate Fix

- Specific code changes to fix the bug
- Before/after code snippets
- Files to modify

### 5.2 Robustness Improvements

- Validation/guards to prevent recurrence
- Type safety improvements (Pydantic models, type hints)
- Error handling additions

### 5.3 Testing Strategy

- Manual verification steps
- Edge cases to test
- Potential automated tests (`pytest` for `apps/api`)

---

## Phase 6: Generate Bug Report

**AI Task:** Create a comprehensive report based on bug type:

````markdown
## Bug Report: [Brief Title]

### Classification

- **Type:** [Client-Side | Server-Side | Full-Stack]
- **Severity:** [Critical | High | Medium | Low]
- **Affected Layer:** [UI | API | Service | Agent | Repository | Database]

### Problem Summary

- **Description:** [What's wrong]
- **Expected:** [What should happen]
- **Actual:** [What happens instead]
- **Reproduction Steps:** [1, 2, 3...]

### Investigation Findings

**Client-Side (if applicable):**

- **Page Observations:** [Data, values, state]
- **Console Errors:** [If any]
- **Network Requests:** [Failed or unusual requests]

**Server-Side (if applicable):**

- **Server Logs:** [Errors, stack traces, correlation IDs]
- **API Response:** [Status code, error message, payload]
- **Database State:** [Row values, missing data, incorrect references]
- **Agent/Task Status:** [Stage state, failures, input payload]

### Root Cause

- **Location:** `[file:line]`
- **Layer:** [Route | Dependency | Service | Agent | Repository | Schema]
- **Problem:** [Why it breaks]
- **Code:**
  ```python
  # Problematic code
  ```
````

### Proposed Fix

- **Strategy:** [Approach]
- **Files to Modify:**
  | File | Layer | Change |
  |------|-------|--------|
  | ... | ... | ... |

- **Before/After:**
  ```python
  # Before
  ```
  ```python
  # After
  ```

### Validation

**Code Quality:**

- [ ] `ruff check` (`apps/api`)
- [ ] `pytest` (`apps/api`)
- [ ] `pnpm --filter web run typecheck` / `lint` (if `apps/web` touched)

**Client-Side Verification (if applicable):**

- [ ] Page renders correctly
- [ ] Console free of errors
- [ ] Network requests succeed

**Server-Side Verification (if applicable):**

- [ ] API returns correct response
- [ ] Database state is correct
- [ ] Server logs show no errors
- [ ] Agent/background task completes (if applicable)

### Next Steps

1. [ ] Implement fix
2. [ ] Run validation commands
3. [ ] Verify fix (browser and/or API)
4. [ ] Check for related patterns that need similar fixes

---

## Output

Return the bug report and ask based on PRD assessment:

**If PRD was created:**

> "I've completed the investigation and created a PRD at `[path]`. Would you like me to:
>
> 1. Implement Phase 1 of the PRD
> 2. Review/refine the PRD first"

**If no PRD needed:**

> "I've completed the investigation. Would you like me to implement the fix?"

Done.
