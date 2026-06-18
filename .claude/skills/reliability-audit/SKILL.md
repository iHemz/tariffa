---
name: reliability-audit
description: Identify likely failures, gaps, and missing tests for a feature or module. Produces a prioritized test plan to connect the dots before shipping.
argument-hint: "[feature | module-path | 'all']"

---

# Reliability Audit: Failure Analysis & Test Gap Discovery

Analyze a feature, module, or the full project for likely failures, implementation gaps, and missing tests. Produces a prioritized, actionable test plan.

This is tariffa — an AI agent pipeline that extracts data from invoices/packing lists, classifies goods against HS codes and regulators (NAFDAC, SON), flags compliance issues, and drafts a Form M prep sheet. It drafts and pre-checks only; it never submits to any government system. Reliability matters because a missed compliance flag or a bad extraction is what causes a port delay.

**Input:** $ARGUMENTS — Target scope: a feature name, a module path (e.g., `apps/api/agents/classifier`), or `all` for project-wide analysis.

---

## Step 1: Determine Scope

Parse `$ARGUMENTS`:

- **Feature name** — Find the related modules and spec docs under `/docs/`
- **Module path** (e.g., `apps/api/agents/classifier`) — Audit that specific module
- **`all`** — Project-wide: audit each agent in the pipeline sequentially
- **Empty** — Ask what to audit

If scope is `all`, process each area sequentially (do NOT spawn parallel agents for `all` — context carries between areas).

---

## Step 2: Gather Context

Before auditing, gather the relevant context:

1. Read the matching spec under `/docs/` (e.g., `docs/03-agent-pipeline.md` for an agent, `docs/04-data-models.md` for the typed contracts)
2. List all files in the target module(s) using Glob
3. List existing test files in the target area (`apps/api` uses pytest; `apps/web` uses its own test setup)
4. Check for any reference fixtures or sample documents

Build a context summary:

```
SCOPE: [feature/module]
SPEC: [path to spec under /docs/, or "none"]
MODULE PATH: [path to module directory]
FILES: [count of source files]
EXISTING TESTS: [count and paths]
FIXTURE DATA: [paths to any test fixtures or sample invoices/packing lists]
STATUS: [Not started / Partial / Complete]
```

---

## Step 3: Run the Reliability Audit

Work through the target area directly, applying all five failure lenses:

1. Read all source files in the target area
2. Read the spec to understand expected behavior
3. Read existing tests to understand current coverage
4. Apply the five failure lenses:
   - **Contracts** — Do the Pydantic models match what's actually produced/consumed at each pipeline handoff? Any drift between `docs/04-data-models.md` and the code?
   - **State/concurrency** — Background tasks, DB writes, S3 uploads, presigned-URL flows
   - **Edge cases** — Malformed or partial invoices, missing fields, unexpected HS codes, empty extraction results, regulator lookups with no match
   - **Integration** — LLM calls (Claude API), pgvector retrieval for the compliance RAG, S3, Postgres
   - **Test coverage** — What would catch a regression if someone changes this code later?
5. Produce the full audit report with prioritized test specifications

Focus especially on:
- What will actually break in production (P0)
- What's missing between spec and implementation
- Compliance grounding: the compliance agent must rely on retrieved regulatory text, never the model's own knowledge — flag any path where that grounding is bypassed

---

## Step 4: Review & Enrich Results

After the pass:

1. **Validate P0 items** — Confirm these are genuinely production-breaking, not theoretical
2. **Check for duplicates** — Ensure recommended tests don't already exist
3. **Add fixture references** — Link test specs to existing sample documents where available
4. **Estimate effort** — Add rough size (S/M/L) to each test spec based on complexity

---

## Step 5: Save Report

Save the audit report under `/docs/audits/`:

```
docs/audits/reliability-audit-[target]-[date].md
```

Example: `docs/audits/reliability-audit-classifier-2026-06-18.md`

---

## Step 6: Present Summary & Next Steps

Present:

```markdown
# Reliability Audit Complete: [Target]

## Risk Summary
- **P0 (Will break):** [count] items
- **P1 (Likely to break):** [count] items
- **P2 (Edge cases):** [count] items
- **P3 (Hardening):** [count] items

## Top 3 Risks
1. [Most critical failure mode]
2. [Second most critical]
3. [Third most critical]

## Test Plan
- **Tests to write:** [count]
- **Estimated effort:** [S/M/L]
- **Recommended order:** [first test to write]

## Gaps Found
- **Missing code:** [count of unimplemented items from spec]
- **Missing tests:** [count of untested critical paths]
- **Contract mismatches:** [count of schema/type drift issues]

Report saved to: `docs/audits/reliability-audit-[target]-[date].md`
```

Then ask:

"Would you like me to:
1. **Start writing the P0 tests** — Implement the highest-priority tests now
2. **Create GitHub issues** — File issues for each gap
3. **Audit another area** — Run on a different target
4. **Implement missing code** — Build the gaps identified in the audit"

---

## Usage Examples

### Audit a specific module
```
/reliability-audit apps/api/agents/classifier
```

### Audit a feature
```
/reliability-audit form-m-prep-sheet
```

### Audit the whole pipeline
```
/reliability-audit all
```

---

## When to Use

- **Before starting implementation** — Know what tests to write first (test-driven)
- **After completing a feature** — Verify nothing was missed before shipping
- **Before a PR** — Final reliability check
- **When revisiting old code** — Understand what's tested and what isn't

---

## Critical Rules

- **REPORT FIRST** — Never start writing tests or code without showing the audit first
- **CONCRETE** — Every test spec must have real input data and assertions
- **PRIORITIZED** — P0 means "will actually break", not "would be nice to test"
- **PATTERN-AWARE** — Recommend tests using existing codebase patterns (pytest fixtures, fakes, dependency injection)
- **GROUND THE COMPLIANCE PATH** — Flag any compliance check that isn't grounded in retrieved regulatory text
- **SAVE THE REPORT** — Always persist to `docs/audits/` for future reference
