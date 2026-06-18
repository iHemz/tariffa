---
name: batch-prd
description: Batch PRD Generator

---

# Batch PRD Generator

Generate separate Product Requirements Documents (PRDs) for multiple features/tasks. Each PRD is created independently with a fresh context. Questions are captured as Open Questions within each PRD rather than asked in chat.

## Input

- `{{tasks}}` - Array of task descriptions (e.g., `["Add upload progress UI", "Extract HS code candidates from invoice", "Draft Form M prep sheet export"]`)
- `{{depth}}` - PRD detail level: `quick` | `standard` (default) | `comprehensive`

## How This Works

1. For each task in `{{tasks}}`, a separate PRD is generated
2. Discovery questions are added to the **Open Questions** section (not asked in chat)
3. After completing each PRD, **clear context and start fresh** for the next one
4. Each PRD is self-contained and can be reviewed/refined independently

## Steps

### 1. Parse and Validate Tasks

**AI Task:** Parse the `{{tasks}}` input:

1. **Validate input:**
   - Ensure `{{tasks}}` is an array of strings
   - Each task should be a brief description (1-3 sentences)
   - Minimum 1 task required

2. **Display task list:**

   ```
   ## Batch PRD Generation

   I'll create separate PRDs for the following tasks:

   1. [Task 1 description]
   2. [Task 2 description]
   3. [Task 3 description]
   ...

   **Depth:** {{depth}}

   Starting with Task 1...
   ```

3. **Proceed to Step 2 for the first task**

### 2. Analyze Single Task

**AI Task:** For the current task, analyze and gather context:

1. **Identify the feature type:**
   - New feature / Enhancement / Bug fix / Refactor / Infrastructure

2. **Search for related code:**
   - Search the codebase for existing implementations (`apps/api` for agents/services, `apps/web` for UI)
   - Identify affected modules, services, and components
   - Note any existing patterns to follow

3. **Check documentation:**
   - Search `/docs/` for relevant architecture or specs (`01-product-vision.md` … `07-repository-setup.md`)

4. **Generate discovery questions** (do NOT ask in chat - these go to Open Questions):
   - Based on information gaps, generate 3-6 questions
   - Categorize them by: Problem & Context, Users & Scope, Requirements, Technical, UX & Design

### 3. Generate PRD for Current Task

**AI Task:** Create the PRD. Adapt section depth based on `{{depth}}`:

- **quick**: Overview, Problem, Requirements, Acceptance Criteria, Open Questions only
- **standard**: All sections, moderate detail
- **comprehensive**: All sections with extensive detail, examples, and edge cases

````markdown
# PRD: [Feature Name]

**Task:** [Original task description from input]
**Author:** AI-Generated | **Date:** [today's date]
**Type:** [New Feature / Enhancement / Bug Fix / Refactor / Infrastructure]
**Depth:** [quick/standard/comprehensive]

---

## Executive Summary

[2-3 paragraph summary covering:]

- What this feature does and why it matters
- Core value proposition
- MVP goal statement

## Problem Statement

[What problem are we solving? What pain point exists today?]

**Current State:** [How things work now - inferred from codebase]
**Desired State:** [How things should work after implementation]

## Target Users

| Persona                      | Description         | Key Needs             |
| ---------------------------- | ------------------- | --------------------- |
| [e.g., Clearing agent]       | [Brief description] | [Primary pain points] |
| [e.g., Freight forwarder]    | [Brief description] | [Primary pain points] |

**Technical Comfort Level:** [Low / Medium / High]

## Goals & Success Metrics

- **Primary Goal:** [What we're trying to achieve]
- **Success Metrics:**
  - [ ] [Measurable outcome 1]
  - [ ] [Measurable outcome 2]
  - [ ] [Measurable outcome 3]

## Scope

### In Scope (MVP)

**Core Functionality:**

- [ ] [Requirement 1]
- [ ] [Requirement 2]

**Technical:**

- [ ] [Technical requirement 1]
- [ ] [Technical requirement 2]

### Out of Scope

- [ ] [Explicitly excluded feature 1]
- [ ] [Explicitly excluded feature 2]
- [ ] [Future enhancement deferred]

## User Stories

### Primary Stories

1. **As a** [user type], **I want to** [action], **so that** [benefit]
   - _Example:_ [Concrete scenario]

2. **As a** [user type], **I want to** [action], **so that** [benefit]
   - _Example:_ [Concrete scenario]

### Edge Cases

- **As a** [user type], **when** [edge condition], **I expect** [behavior]

## Functional Requirements

### Must Have (P0)

- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Should Have (P1)

- [ ] [Secondary requirement]
- [ ] [Secondary requirement]

### Nice to Have (P2)

- [ ] [Optional enhancement]

## Technical Approach

### Affected Areas

| Area                         | Changes        | Impact         |
| ---------------------------- | -------------- | -------------- |
| `apps/api/[module]`          | [what changes] | [High/Med/Low] |
| `apps/api/[route]`           | [what changes] | [High/Med/Low] |
| `apps/web/[component]`       | [what changes] | [High/Med/Low] |

### Architecture & Patterns

[Based on codebase search - patterns to follow, services to use]

**Design Patterns:**

- [Pattern 1 from existing codebase]
- [Pattern 2 to follow]

**Key Principles:**

- All business logic, validation, and AI orchestration live in `apps/api` — the frontend is a thin client
- Every agent-to-agent handoff is a typed Pydantic model, validated before passing downstream
- Compliance logic must be grounded in retrieved regulatory text (RAG), not model memory
- Code new features for reuse: generic interfaces, minimal coupling

### Backend Considerations (`apps/api`)

**Schema / Data Updates:**

```python
# Example Pydantic / SQLAlchemy changes
class ExampleModel(BaseModel):
    field_name: str
```

**New tables / columns:** [List any Postgres schema changes]
**Migrations Required:** [Yes/No - describe if yes]
**Background tasks:** [Any FastAPI background tasks needed?]

### API Changes

**New Endpoints:**

| Method | Endpoint          | Description   |
| ------ | ----------------- | ------------- |
| POST   | `/api/[resource]` | [Description] |
| GET    | `/api/[resource]` | [Description] |

**Request/Response Example:**

```json
// POST /api/example
{
  "field": "value"
}
```

### Technology Stack

| Layer      | Technology              | Notes                       |
| ---------- | ----------------------- | --------------------------- |
| Frontend   | Next.js 16, React 19    | Thin client, App Router     |
| UI         | Tailwind CSS v4         | [specific components]       |
| Data fetch | TanStack Query          | [queries affected]          |
| Backend    | FastAPI, Pydantic AI    | [agents/services affected]  |
| Database   | Postgres + pgvector     | [tables affected]           |
| Validation | Pydantic                | [models affected]           |
| Async      | FastAPI background tasks| [if async workflows needed] |

## Security & Configuration

### Authorization

- **Auth:** [Which routes require auth? Simple auth via the API]
- **User-facing impact:** [Clearing agent, freight forwarder, etc.]

### Configuration

| Variable    | Purpose   | Required |
| ----------- | --------- | -------- |
| `[ENV_VAR]` | [Purpose] | Yes/No   |

### Security Considerations

- [ ] Input validation via Pydantic models
- [ ] Auth checks on protected routes
- [ ] No sensitive data or LLM keys in client bundles
- [ ] This tool drafts and pre-checks only — it never submits to NICIS / Trade Window

## Design Input

> This section captures design requirements and considerations. Review before engineering implementation begins.

### Design Required?

- **Requires Design Work:** [Yes / No / Partial]
- **Design Type:** [New UI / UI Enhancement / No UI Changes / Backend Only]

### Visual & Interaction Design

**UI Components Affected:**

- [ ] [Component/Screen 1]
- [ ] [Component/Screen 2]

**Design Considerations:**

- [ ] [Consideration 1 - e.g., "How should empty states be handled?"]
- [ ] [Consideration 2 - e.g., "Mobile responsiveness requirements"]
- [ ] [Consideration 3 - e.g., "Accessibility needs"]

### User Experience

**User Flow:**

1. [Step 1 of the user journey]
2. [Step 2 of the user journey]
3. [Step 3 of the user journey]

**Edge Cases to Design For:**

- [ ] [Edge case 1 - e.g., "What if extraction returns no line items?"]
- [ ] [Edge case 2 - e.g., "What if a compliance check is inconclusive?"]
- [ ] [Edge case 3 - e.g., "What if data is loading?"]

### Design Questions

- [ ] [Design question 1]
- [ ] [Design question 2]
- [ ] [Design question 3]

## Implementation Phases

### Phase 1: Foundation

**Goal:** [What this phase achieves]
**Deliverables:**

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Validation:** [How to verify completion]

### Phase 2: Core Features

**Goal:** [What this phase achieves]
**Deliverables:**

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Validation:** [How to verify completion]

### Phase 3: Polish & Integration

**Goal:** [What this phase achieves]
**Deliverables:**

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Validation:** [How to verify completion]

## Dependencies & Risks

### Dependencies

| Dependency     | Type              | Status          |
| -------------- | ----------------- | --------------- |
| [Dependency 1] | External/Internal | [Ready/Blocked] |

### Risks & Mitigations

| Risk     | Impact       | Likelihood   | Mitigation       |
| -------- | ------------ | ------------ | ---------------- |
| [Risk 1] | High/Med/Low | High/Med/Low | [How to address] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to address] |

## Future Considerations

[Post-MVP enhancements and integration opportunities]

- [ ] [Future feature 1]
- [ ] [Future feature 2]
- [ ] [Integration opportunity]

## Open Questions

> **Important:** These questions were identified during PRD generation and should be answered before implementation begins. Review and answer each question, then update the relevant sections of this PRD.

### Problem & Context

- [ ] [Question about the specific problem or pain point]
- [ ] [Question about current workarounds]
- [ ] [Question about what triggered this need]

### Users & Scope

- [ ] [Question about primary users]
- [ ] [Question about user segments or frequency]

### Requirements

- [ ] [Question about success criteria]
- [ ] [Question about must-haves vs nice-to-haves]
- [ ] [Question about explicit exclusions]

### Technical

- [ ] [Question about integrations with existing features]
- [ ] [Question about performance or scale considerations]

### UX & Design

- [ ] [Question about UI placement]
- [ ] [Question about reference implementations or patterns]
- [ ] [Question about design input needs before engineering]

---

**Questions Answered:** [ ] / [total]
**Ready for Implementation:** No (Answer open questions first)

## Acceptance Criteria

[Must be testable - refine after answering Open Questions]

### Functional Criteria

- [ ] [Criterion 1 - specific, measurable]
- [ ] [Criterion 2 - specific, measurable]
- [ ] [Criterion 3 - specific, measurable]

### Quality Criteria

**Frontend (`apps/web`):**

- [ ] Types pass (`pnpm --filter web run typecheck`)
- [ ] Lint passes (`pnpm --filter web run lint`)

**Backend (`apps/api`):**

- [ ] Lint passes (`ruff check`)
- [ ] Tests pass (`pytest`)
- [ ] Every pipeline handoff is a validated Pydantic model
- [ ] Compliance logic is RAG-grounded
- [ ] Follows project conventions and patterns

### UX Criteria

- [ ] [UX requirement 1]
- [ ] [UX requirement 2]

---

_Generated via Batch PRD on [date] | Task [N] of [total]_
````

### 4. Save PRD File

**AI Task:** Save the PRD:

1. Generate a slug from the task description (kebab-case, max 50 chars)
2. Create file at `docs/prds/batch-[date]-[task-slug].md`
3. Ensure `docs/prds/` directory exists (create if needed)

**Example:** Task "Draft Form M prep sheet export" → `docs/prds/batch-2026-06-18-draft-form-m-prep-sheet-export.md`

### 5. Output Task Completion

**AI Task:** After saving the PRD, output:

```
## PRD Created (Task [N] of [total])

**File:** `docs/prds/batch-[date]-[task-slug].md`
**Task:** [Task description]
**Depth:** [quick/standard/comprehensive]

**Key Requirements (P0):**
- [Top 3 must-have requirements]

**Open Questions:** [count] items need answering before implementation

---

**CLEAR CONTEXT NOW** before proceeding to the next task.

**Next:** Task [N+1]: "[Next task description]"

Say "continue" after clearing context to generate the next PRD.
```

### 6. Handle Remaining Tasks

**AI Task:** After context is cleared and user says "continue":

1. **Acknowledge fresh context:**

   ```
   Starting fresh with Task [N+1] of [total]:
   "[Task description]"
   ```

2. **Repeat Steps 2-5** for the next task

3. **Continue until all tasks are complete**

### 7. Final Summary (After All Tasks)

**AI Task:** When all PRDs are generated, output:

```
## Batch PRD Generation Complete

**Total PRDs Created:** [count]
**Depth:** [quick/standard/comprehensive]

| # | Task | File | Open Questions |
|---|------|------|----------------|
| 1 | [Task 1] | `docs/prds/[file1].md` | [count] |
| 2 | [Task 2] | `docs/prds/[file2].md` | [count] |
| 3 | [Task 3] | `docs/prds/[file3].md` | [count] |

**Next Steps:**
1. Review each PRD for accuracy
2. Answer Open Questions in each document
3. Mark "Ready for Implementation: Yes" when questions are answered
4. Prioritize implementation order

**Tip:** Use the standard `prd` command if you want conversational discovery for any specific feature.
```

Done.

## Question Generation Guidelines

When generating Open Questions for each PRD, follow these rules:

### Question Categories

**Problem & Context (always include 1-2):**

- "What specific problem or pain point does this solve?"
- "What's the current workaround users have to do today?"
- "What triggered the need for this feature now?"

**Users & Scope (always include 1-2):**

- "Who are the primary users of this feature?"
- "Is this for all users or a specific segment?"
- "What's the expected usage frequency?"

**Requirements (include based on gaps):**

- "What does success look like for this feature?"
- "Are there any must-have requirements vs nice-to-haves?"
- "Are there any explicit things this should NOT do?"

**Technical (include if technical ambiguity):**

- "Does this need to integrate with any existing features?"
- "Are there any performance or scale considerations?"

**UX & Design (include for user-facing features):**

- "Do you have any preferences for where this lives in the UI?"
- "Are there similar features in other products we should reference?"
- "Does this feature need design input before engineering starts?"

### Question Selection Rules

- **Minimum 3 questions, maximum 8** per PRD
- **Always include** at least 1 Problem & Context + 1 Users & Scope question
- **For vague tasks:** More Problem & Context questions
- **For technical tasks:** More Technical questions
- **For UI features:** More UX & Design questions
- **Never ask questions** that can be answered from codebase analysis
- **Be specific** - tailor questions to the actual task

## Example Usage

**Input:**

```
{{tasks}}: ["Add upload progress UI for invoices", "Extract HS code candidates from packing lists", "Flag NAFDAC/SON compliance issues in the review screen"]
{{depth}}: standard
```

**Output:** Three separate PRDs in `docs/prds/`:

1. `batch-2026-06-18-add-upload-progress-ui-for-invoices.md`
2. `batch-2026-06-18-extract-hs-code-candidates-from-packing-lists.md`
3. `batch-2026-06-18-flag-nafdac-son-compliance-issues-in-the-review-screen.md`

Each PRD contains Open Questions specific to that feature, ready for review.
