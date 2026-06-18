# tariffa — agent toolkit instructions

This file orients you inside `.claude/`. The project overview, architecture, and
non-negotiables live in the **root `CLAUDE.md`** — read that first; it's the source of truth.

## Quick reference

- **Frontend** (`apps/web`): Next.js 16, React 19, Tailwind CSS v4, TanStack Query, react-dropzone. Package manager **pnpm**. Thin client — no business logic, never talks to Postgres/S3/Claude directly.
- **Backend** (`apps/api`): Python FastAPI, Pydantic AI, Postgres + pgvector, S3, Claude API. Tooling **uv**, **ruff**, **pytest**. Owns all agent orchestration, the database, file storage, and every LLM call.
- **Specs**: detailed docs live in `/docs/` (`01-product-vision.md` … `07-repository-setup.md`). Read the relevant one before working on that area.

## How `.claude/` is organised

- `rules/` — coding conventions, auto-loaded per file path. Read them before writing code in the matching area.
- `agents/` — specialised subagents (code-review, refactor-agent, reliability-auditor, prd-writer, etc.).
- `skills/` — slash-command workflows (`/commit`, `/ship`, `/prd`, `/refactor`, `/code-quality-review`, …).
- `commands/` — `/sod`, `/eod`, and a couple of project commands.
- `VALUES.md` — how I think about building tariffa. When a decision is ambiguous, default to what's written there.
- `memory/ROUTING.md` — where the authoritative answer lives for each concern when sources conflict.

## Git workflow

**Never commit or push directly to `main`.** Branch first:

1. Check the branch with `git branch --show-current`.
2. If on `main`, create one: `git checkout -b <type>/<description>`.
3. Stage, commit, push, open a PR — or use `/ship`.

This applies to every change, no matter how small.

## Quality gate

A pre-commit hook (`.husky/pre-commit`) enforces the gate locally. Before declaring any work done:

- `pnpm --filter web run typecheck` and `pnpm --filter web run lint` pass with zero errors.
- `ruff check` and `ruff format --check` pass on `apps/api`; `pytest` is green for new backend logic.
- Every agent-to-agent handoff is a validated **Pydantic** model — no raw dicts crossing a pipeline boundary.
- The compliance agent is grounded in retrieved regulatory text (RAG), never the model's unverified knowledge.
- tariffa **drafts and pre-checks only** — it never claims to submit to NICIS, Trade Window, or any government system.

See `.claude/rules/production-quality-gate.md` for the full pre-PR checklist.
