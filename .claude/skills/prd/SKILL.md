---
name: prd
description: Create a comprehensive Product Requirements Document from direct input. Includes discovery questions, codebase analysis, and quality criteria.
argument-hint: "[feature description]"

---

# Create PRD

Generate a comprehensive Product Requirements Document (PRD) enriched with codebase context.

**Maintainability Mindset:** Even as a solo founder, write so that future-me (or a first hire) can pick up, extend, and reason about the feature without spelunking. Favour clear contracts and typed boundaries over cleverness.

**First-Use Mindset:** Imagine a Nigerian freight forwarder or clearing agent trying this for the first time. They have never seen this product, do not know our jargon, and will not read documentation. Every requirement, flow, and acceptance criterion must hold up under that lens — if a first-time user cannot succeed without help, the PRD is incomplete.

**Input:** $ARGUMENTS — A feature description, or leave blank to be prompted.

## Steps

### 1. Determine Input Source

1. **If a feature description is provided in $ARGUMENTS:**
   - Use the provided text as the feature source

2. **If $ARGUMENTS is empty:**
   - Ask: "Please describe the feature you'd like to build."

### 2. Requirements Discovery (Conversational)

Before generating the PRD, engage in discovery. This is NOT optional.

1. **Summarize understanding** (1-2 sentences)
2. **Ask 4-5 targeted questions** from these categories:
   - Problem & Context (what pain point, current workarounds)
   - Users & Scope (who uses it — forwarders, clearing agents — frequency)
   - Requirements (success criteria, must-haves vs nice-to-haves)
   - Technical (integrations, performance considerations)
   - UX & Design (UI placement, reference implementations, design input needed)
   - Figma Design: "Do you have a Figma design for this feature? Provide the URL (figma.com/design/...) or say 'none'."
3. **Wait for responses** before proceeding
4. **Auto-populate from OUTCOMES.md:** If `figma_url` exists on the relevant outcome in `docs/OUTCOMES.md`, use it automatically and confirm with me.
5. **Confirm understanding** with a brief summary, get my approval

### 3. Search Codebase Context

1. Search for related code — existing implementations, affected modules, patterns to follow
2. Check `docs/` for relevant specs (`docs/02-architecture.md`, `docs/03-agent-pipeline.md`, `docs/04-data-models.md`)
3. Note the relevant boundaries: `apps/web` is a thin Next.js client (no business logic, never talks to DB/S3/LLM directly); `apps/api` owns all agent orchestration, DB, storage, and LLM calls. Every agent-to-agent handoff is a typed Pydantic model.

### 4. Generate PRD

Create PRD with these sections:

**Frontmatter** — Include at the top of every PRD:
```markdown
**Date:** [date]
**Status:** Draft
**Type:** [Feature / Infrastructure / Refactor]
**Priority:** [P0-P3]
**ui_heavy:** [true/false]
**Figma Design:** [URL or N/A]
```

**Enforcement:** When `ui_heavy: true` and `Figma Design` is `N/A` or missing, emit a warning in the PRD:
> ⚠️ UI-heavy PRD without Figma reference. Design accuracy cannot be guaranteed.

**Sections:**
- Executive Summary, Problem Statement, Target Users
- Goals & Success Metrics, Scope (In/Out), User Stories
- Functional Requirements (P0/P1/P2)
- Technical Approach (affected modules, architecture patterns, Pydantic model boundaries, DB changes, API changes)
- Security & Configuration, Design Input
- Maintainability (clear contracts, typed handoffs, docs that survive a handoff to a first hire)
- Implementation Phases (Foundation → Core → Polish)
- Dependencies & Risks, Future Considerations, Open Questions
- Human Acceptance Test, Acceptance Criteria (Functional + Quality + UX)

### 5. Save PRD

1. **Check for existing PRDs** in `docs/prds/` with similar names first
2. Save to: `docs/prds/[DD-MM-YY]/[feature-slug].md`
3. Use kebab-case, create directory if needed

### 6. Output Confirmation

```
## PRD Created

**File:** `docs/prds/[path]`
**Feature:** [Name]
**Key Requirements (P0):** [top 3]
**Design Required:** [Yes/No/Partial]
**Open Questions:** [count]

**Next Steps:**
1. Review PRD for accuracy
2. Answer open questions
3. Start with the Foundation phase
```
