---
name: architect
description: Generate an Architecture Decision Document (ADD) from a feature spec. Explores multiple approaches and recommends an optimal design with extractability in mind.
argument-hint: "[path-to-spec]"

---

# Architect: Design Architecture from a Spec

Generate an Architecture Decision Document (ADD) that complements a feature spec. Analyzes requirements, explores multiple architectural approaches, and recommends the optimal design with modularity and clear service boundaries in mind.

**Design philosophy:** Favor generic interfaces and minimal coupling so a component could later be lifted out or reused. In tariffa terms: keep each agent stage (extraction, classification, compliance, Form M draft) behind a typed Pydantic contract so it can be tested and swapped independently.

**Input:** $ARGUMENTS — Path to the spec file (e.g., `/docs/03-agent-pipeline.md` or a local TODO note describing the feature).

## Steps

### 1. Validate the Spec

1. If $ARGUMENTS is provided, read the spec file.
2. If not provided, ask the user to point at the relevant doc under `/docs/` (the canonical specs are `/docs/01-product-vision.md` … `/docs/07-repository-setup.md`) or to describe the feature inline.
3. If the spec is incomplete, note the gaps and ask whether to continue.

### 2. Parse the Requirements

Extract: core requirements, constraints (service boundaries — `apps/web` is a thin client, all logic lives in `apps/api`), scale indicators, technology requirements.

### 3. Architectural Discovery (Conversational)

1. Summarize the feature and its core technical challenge.
2. Ask 4-5 targeted questions about: reusability, boundaries/interfaces (Pydantic contracts between stages), state/data (Postgres + pgvector), integration points (S3, Claude API), complexity trade-offs, pattern preferences.
3. Wait for responses, follow up if needed.
4. Confirm understanding before designing.

### 4. Analyze Codebase Context

1. Search for similar patterns in existing code (`apps/api` for agents/services, `apps/web` for UI).
2. Review the relevant `/docs/` spec for the area being touched.
3. Check for reusable utilities, base classes, and existing Pydantic models in `apps/api`.
4. Note the non-negotiables: typed Pydantic handoffs between pipeline stages, RAG-grounded compliance, no business logic in the frontend, browser → S3 direct uploads.

### 5. Generate 2-4 Architectural Options

For each option provide:
- Name, core concept, ASCII architecture diagram
- Key abstractions and module structure (Python Protocol ports / Pydantic models / FastAPI routers)
- Reusability potential (standalone package / internal module / project-specific)
- Trade-offs table (simplicity, flexibility, reusability, time to MVP, maintenance, testing)
- Risks

### 6. Present Options with Recommendation

Show a comparison table and recommend an option. Wait for selection.

### 7. Deep Dive Selected Option

Elaborate: detailed component design, data flow, integration spec, file-by-file implementation guide, and the typed contracts (Pydantic models) at each boundary.

### 8. Save the ADD

- Save under `/docs/decisions/` (create the folder if it does not exist) as `add-[feature-slug].md`.
- Include: Context, Decision Drivers, Options Considered, Decision, Architecture Overview, Core Abstractions, Module Structure, Integration Points, Reusability Notes, Implementation Sequence, Consequences, Review Checklist.
- **End with a `## Contract Checklist`.** Enumerate every port, API route, and pipeline handoff as a concrete failing-test name (`pytest`) to write before any implementation, plus one first-run target per key user flow. If you cannot name a concrete test for each contract, the ADD is under-specified — revise it.

### 9. Output Confirmation

```
## Architecture Decision Document Created

**ADD:** `[path]`
**Spec:** `[spec_path]`
**Decision:** Option [X] - [Name]
**Reusability:** [High/Medium/Low]

**Next steps:**
1. Review the ADD
2. Write the contract tests listed in the Contract Checklist
3. Begin implementation
```
