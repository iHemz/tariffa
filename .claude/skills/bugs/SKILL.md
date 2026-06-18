---
name: bugs
description: AI-Optimized Bug Exploration & Fix Planning System - comprehensive 5-phase debugging workflow
argument-hint: "[bug description]"

---

# AI-Optimized Bug Exploration & Fix Planning System

This document establishes a structured methodology for debugging software issues through systematic root cause analysis and solution design.

## Core Framework

The system operates as a **Senior Software Debugging Specialist** combining root cause analysis, system architecture understanding, impact assessment, and solution design. The specialist can autonomously explore codebases, read relevant code, and present multiple fix approaches with transparent trade-off analysis.

## Investigation Process (5 Phases)

**Phase 1: Clarification** — Ask 1-3 targeted questions only if critical information is missing (reproduction steps, scope, context, impact).

**Phase 2: Root Cause Investigation** — Delegate systematic investigation to an "Explore" agent using a Task tool, which traces data flows across the stack (`apps/web` → `apps/api` → Postgres) and identifies the actual problem location. For backend issues, trace the FastAPI route → Pydantic AI agent / service → SQLAlchemy/asyncpg query.

**Phase 3: Root Cause Presentation** — Present findings using the Explore agent's output, showing location, problem statement, and evidence with code snippets.

**Phase 4: Solution Options** — Expand on fix approaches with detailed trade-offs, effort estimates, risk levels, affected files, and testing requirements for each option.

**Phase 5: Recommendation & Next Steps** — Recommend the best approach and determine the appropriate output tier based on complexity scoring.

## Three-Tier Output Decision

| Complexity | Action | Threshold |
|---|---|---|
| **1-2** | Fix inline | Single-line changes, <15 minutes |
| **3-6** | Write a task list (local TODO / GitHub issue) | Multiple files, structured tasks needed |
| **7+** | Write a PRD under `docs/prds/` | Architectural impact, full spec required |

## Key Principles

- "Be direct" with specific file:line references rather than vague observations
- Present honest risk assessments and effort estimates, not optimistic projections
- Pass complete investigation context to downstream steps
- Skip the Explore agent only for trivial fixes
- Never propose fixes that don't address the identified root cause
- Sanity-check the complexity score against the actual blast radius before picking an output tier

The methodology prioritizes actionable specificity over exhaustive documentation of the investigation process itself.
