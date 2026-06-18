---
name: ux-design
description: Generate a UX design spec from a PRD — page layouts, information architecture, data display, user flows, and interaction patterns.
argument-hint: "[path to PRD]"

---

# UX Design: Layout & Data Spec from PRD

Generate a UX design specification from a PRD. Focuses on **layout structure, information architecture, data display, user flows, and interaction patterns** — not component-level implementation.

**Input:** $ARGUMENTS — Path to a PRD file (e.g., `docs/prds/document-upload.md`)

## Steps

### 1. Load Context

1. **Read the PRD** at the provided path. If $ARGUMENTS is empty, ask the user for the PRD path.
2. **Extract Figma URL** — Look for `**Figma Design:**` in the PRD frontmatter. If a valid Figma URL is present (not `N/A`), store it for Step 2b.
3. **Read existing page structure** — Use the Explore agent to find any existing pages/routes related to this feature:
   ```
   Task(
     description: "Explore existing UI for [feature]",
     subagent_type: "Explore",
     prompt: "Find all pages, routes, and components in apps/web related to [feature keyword].
     Look in app/ for page.tsx files, components/, and any existing flows.
     Also check for related user flows, navigation patterns, and TanStack Query hooks.
     Return: existing pages, data sources (API hooks calling apps/api), navigation structure."
   )
   ```

### 2. Analyze PRD Requirements

Extract from the PRD:
- **User stories** — What does the user need to do?
- **Data entities** — What data is displayed, collected, or transformed?
- **User flows** — What are the step-by-step journeys?
- **Success metrics** — What does good UX look like for these metrics?
- **Constraints** — Auth requirements, performance targets, device targets

### 2b. Figma Design Enrichment (Conditional)

**When `figma_url` is present in the PRD:**

1. Parse the Figma URL to extract `fileKey` and `nodeId`:
   - `figma.com/design/:fileKey/:fileName?node-id=:nodeId` — convert `-` to `:` in nodeId
   - `figma.com/make/:fileKey/:fileName` — use fileKey, nodeId may be absent

2. Call Figma MCP tools (graceful fallback — if any call fails, log warning and continue with text-only spec):

   ```
   Tool: get_design_context
   Arguments: { fileKey, nodeId }
   → Extract: layout structure, component hierarchy, code hints
   ```

   ```
   Tool: get_variable_defs
   Arguments: { fileKey }
   → Extract: design tokens (colors, spacing, typography variables)
   ```

   ```
   Tool: get_code_connect_suggestions
   Arguments: { fileKey, nodeId }
   → Extract: component mappings (Figma component → codebase component)
   ```

3. Read the Tailwind CSS v4 theme (the `@theme` block in `apps/web/app/globals.css`, or the project's CSS token definitions) to load the design tokens.

4. Generate a **token reconciliation table**: map each Figma token to the nearest Tailwind v4 token / utility.
   - Exact matches: map directly (e.g., Figma `#5196fe` → `--color-primary-500` / `bg-primary-500`)
   - No match: flag as discrepancy with recommendation (e.g., "Figma uses `#3B82F6` — nearest theme token: `--color-primary-500`. Use `bg-primary-500`.")
   - Never recommend raw hex values — always map to semantic Tailwind tokens.

5. Generate a **component mapping table**: map Figma component names to codebase component paths.
   - If Code Connect data is available: use it directly
   - If not: recommend the closest existing component or Tailwind composition (e.g., "Hero Card" → a `<div>` with Tailwind card/stack utilities)

**When `figma_url` is absent:** Skip this step entirely. Generate text-only spec as today (backward compatible).

### 3. Generate UX Design Spec

Output a markdown document saved to `docs/ux/[feature-slug].md` with these sections:

```markdown
# UX Design: [Feature Name]

**PRD:** [path to PRD]
**Figma Design:** [url or N/A]
**Created:** [date]
**Status:** Draft

---

## 0. Visual Design Context (only when Figma URL present)

### Token Reconciliation

| Figma Token | Figma Value | Tailwind Token | Match |
|-------------|-------------|----------------|-------|
| Primary Blue | #5196fe | --color-primary-500 / bg-primary-500 | Exact |
| Background | #F8F9FA | --color-gray-50 / bg-gray-50 | Exact |
| Heading Size | 30px | text-3xl (30px) | Exact |
| Card Padding | 24px | p-6 (24px) | Exact |
| [unmapped] | #3B82F6 | --color-primary-500 (nearest) | Discrepancy |

### Component Mapping

| Figma Component | Codebase Component | Notes |
|-----------------|-------------------|-------|
| Feature Card | apps/web/components/[name]/FeatureCard.tsx | Code Connect |
| CTA Button | apps/web/components/ui/Button.tsx | Code Connect |
| Hero Section | — (new component needed) | Compose with Tailwind flex/stack utilities |

### Layout Dimensions
- Container max width: [value]
- Grid: [columns, gap]
- Key breakpoints from Figma: [list]

### Discrepancies
- [List any Figma tokens that don't map to the Tailwind theme — with recommendation for which token to use instead]

---

## 1. Information Architecture

### Site Map / Page Hierarchy
- Where does this feature live in the app navigation?
- What pages/routes are needed?
- How do users navigate between them?

### Content Inventory
| Page/View | Primary Data | Secondary Data | Actions Available |
|-----------|-------------|----------------|-------------------|
| [name]    | [what]      | [what]         | [CTAs, inputs]    |

---

## 2. User Flows

### Flow: [Primary Flow Name]
```
[Step 1: Description] → [Step 2: Description] → [Step 3: Description]
   ↓ (on error)
[Error recovery path]
```

**Entry points:** [How users arrive]
**Exit points:** [Where users go next]
**Decision points:** [Where the flow branches]

[Repeat for each major flow]

---

## 2b. First-Run Checklist (REQUIRED — PR gate input)

This section is the canonical source to replay row-by-row as a first-time user before opening a PR. **It must exist for every UI-heavy feature.** If it's vague, the PR gate is vague — write each row as if a developer who has never seen this feature has to reproduce it.

Walk the flow as a **low-tech-comfort first-timer**: someone who has not read the PRD, does not know the jargon, and will not click around to discover hidden affordances. A row that assumes prior product knowledge or hides async latency is a P0.

| # | Step | Expected UI | Empty / Loading / Error states | Async signal ≤2s? | Mobile (375px) | Desktop (1280px) | P0/P1 |
|---|------|-------------|-------------------------------|---------------------|----------------|------------------|-------|
| 1 | [exact click/tap copy the user sees] | [what renders] | [which states must render and what copy each shows] | [yes + what signal appears] | [must work — tap ≥44px, no horizontal scroll] | [must work] | [severity] |

**Rules:**
- The click path must fit in **≤10 numbered steps** from landing to success state. If it doesn't, the feature is too complex and needs a PRD revision.
- Every async operation (API call, FastAPI background task, AI agent run, S3 file upload) in the flows above must appear here with a visible UI signal ≤2s (spinner, skeleton, optimistic state, toast). Silent latency is a P0.
- Every screen must list which of empty / loading / error / offline states render and what copy + CTA each shows. A missing empty state is a P0.
- Every copy string or CTA label a first-timer could plausibly misread is a P0.
- If the user closes the tab mid-flow, note per step whether the flow is resumable from where they left off.
- Mobile and desktop are **both** gated — tap targets ≥44px, no hover-only affordances, no horizontal scroll at 375px.

[Repeat the table for each major flow]

---

## 3. Page Layouts

### [Page Name]
**URL:** `/path/to/page`
**Auth required:** Yes/No
**Purpose:** [One sentence]

#### Layout Structure
```
┌─────────────────────────────────────────┐
│ [Header / Navigation]                    │
├─────────────────────────────────────────┤
│                                         │
│ [Section 1: Purpose]                    │
│   - What data is shown                  │
│   - What actions are available          │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│ [Section 2: Purpose]                    │
│   - What data is shown                  │
│   - What actions are available          │
│                                         │
├─────────────────────────────────────────┤
│ [Footer / Navigation]                   │
└─────────────────────────────────────────┘
```

#### Data Requirements
| Field/Element | Source | Format | Update Frequency |
|---------------|--------|--------|------------------|
| [name]        | [API/store/static] | [text/number/list/etc] | [real-time/on-load/user-action] |

#### States
- **Loading:** [What the user sees while data loads]
- **Empty:** [What the user sees with no data]
- **Error:** [What the user sees on failure]
- **Success:** [What the user sees on completion]

[Repeat for each page]

---

## 4. Data Flow

### Data Sources
| Data | Source | When Fetched | Cached? |
|------|--------|-------------|---------|
| [name] | [API endpoint / service / store] | [on mount / on action / real-time] | [yes/no] |

### User Input Collection
| Input | Type | Validation | When Collected |
|-------|------|------------|---------------|
| [name] | [text/select/toggle/etc] | [rules] | [which step/page] |

### Data Transformations
- [What data is derived/computed from raw sources]
- [What aggregations or formatting happens client-side]

---

## 5. Interaction Patterns

### Navigation
- [How users move between pages/steps]
- [Back/forward behavior]
- [Deep linking support]

### Progressive Disclosure
- [What's shown immediately vs on demand]
- [Expand/collapse patterns]
- [Multi-step flow progression]

### Feedback & Communication
- [How success is communicated]
- [How errors are communicated]
- [How progress is communicated]
- [How waiting is communicated]

---

## 6. Responsive Behavior

### Mobile (375px)
- [Layout changes]
- [Content priority shifts]
- [Navigation changes]

### Tablet (768px)
- [Layout changes]

### Desktop (1200px+)
- [Full layout description]

---

## 7. Edge Cases & Error States

| Scenario | User Sees | Recovery Action |
|----------|-----------|-----------------|
| [Network failure] | [message] | [retry button / cached data] |
| [Empty data] | [guidance] | [CTA to populate] |
| [Permission denied] | [message] | [upgrade / request access] |
| [Timeout] | [message] | [retry / simplified view] |

---

## 8. Open Questions

- [ ] [Question about layout/data/flow that needs product input]
```

### 4. Present to User

After generating the spec:

1. **Summarize** the key design decisions made
2. **Highlight** any assumptions or open questions
3. **Suggest next steps:**
   - Review and refine the spec
   - Plan the technical architecture (which apps/web pages and apps/api endpoints to build)
   - Do a visual-polish pass after implementation

## Design Principles

When making layout and data decisions, follow these principles:

> **Guiding lens:** Imagine you are a dumb human in 2026 trying to do this task for the first time. They have not read your PRD, do not know your jargon, and will not click around to find what they need. Every label, layout choice, and flow step has to make sense to them on first contact — or you have failed.

1. **Value First** — Show the most valuable information immediately, progressive disclosure for details
2. **Minimum Input** — Collect only what's needed at each step, pre-fill where possible
3. **Clear Hierarchy** — Every page has ONE primary action, supporting secondary actions
4. **State Awareness** — Every view has loading, empty, error, and success states defined
5. **Data Proximity** — Related data and actions are grouped together
6. **Scannable** — Users should understand a page in 3 seconds (headings, visual hierarchy, whitespace)
7. **Recoverable** — Every error state has a clear recovery path
8. **Mobile-Conscious** — Design mobile layout first, expand for desktop (not the reverse)
