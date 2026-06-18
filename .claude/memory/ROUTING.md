# Authority Routing

Where to find the truth for each concern. When sources conflict, higher tiers win.

## Document priority (highest → lowest)

| Tier | Source | Scope |
|------|--------|-------|
| 1 | Root `CLAUDE.md` + `.claude/CLAUDE.md` | Critical rules, architecture boundaries, non-negotiables |
| 2 | `.claude/rules/*.md` | Coding conventions (read before working in the matching area) |
| 3 | `docs/02-architecture.md` | Service boundaries, why Next.js + FastAPI + Pydantic AI |
| 4 | `docs/03-agent-pipeline.md`, `docs/04-data-models.md` | The four agents and the typed Pydantic contracts between them |
| 5 | `docs/01,05,06,07` + `.claude/VALUES.md` | Product vision, build phases, regulatory KB, repo setup, operating principles |

## Where to find patterns

| Building... | Read these first |
|-------------|------------------|
| A pipeline agent | `docs/03-agent-pipeline.md` + `apps/api` agent code |
| A Pydantic stage contract | `docs/04-data-models.md` + `references/patterns/validation.md` |
| A FastAPI route / service | `.claude/rules/api-routes.md` |
| The regulatory RAG knowledge base | `docs/06-regulatory-knowledge-base.md` |
| An LLM call / structured output | `references/ai-provider-configuration.md` + `references/gemini-structured-output-guide.md` |
| A React component / screen | `.claude/rules/cross-device-interactions.md` + `.claude/rules/design-tokens.md` |
| A data-fetching hook (TanStack Query) | `.claude/rules/api-routes.md` (frontend section) |
| Logging | `references/patterns/logging.md` |
| Agent / context architecture | `references/new-agent-architecture/` |

## Non-negotiables (never override)

- Frontend is a thin client. All business logic, validation, and AI orchestration live in `apps/api`.
- Every agent-to-agent handoff is a validated Pydantic model — no raw dicts crossing a boundary.
- The compliance agent is grounded in retrieved regulatory text (RAG), never unverified model knowledge.
- tariffa drafts and pre-checks only — it never submits to NICIS, Trade Window, or any government system.
- Large uploads go browser → S3 via presigned URL — never proxied through both `web` and `api`.
