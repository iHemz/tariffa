# Repository setup

Concrete scaffolding: directory layout, packages, and setup commands for both services. Versions current as of June 2026 — check for newer stable releases before pinning if you're reading this much later.

## Full directory tree

```
tariffa/
├── CLAUDE.md
├── README.md
├── .gitignore
├── docs/
│   ├── 01-product-vision.md
│   ├── 02-architecture.md
│   ├── 03-agent-pipeline.md
│   ├── 04-data-models.md
│   ├── 05-build-phases.md
│   ├── 06-regulatory-knowledge-base.md
│   └── 07-repository-setup.md   ← this file
└── apps/
    ├── web/          ← Next.js frontend
    │   ├── app/
    │   ├── components/
    │   ├── lib/
    │   ├── package.json
    │   └── ...
    └── api/          ← Python FastAPI backend
        ├── src/
        │   ├── agents/        ← the four Pydantic AI agents
        │   │   ├── extraction.py
        │   │   ├── classification.py
        │   │   ├── compliance.py
        │   │   └── form_drafting.py
        │   ├── models/        ← Pydantic schemas (see 04-data-models.md)
        │   ├── kb/            ← regulatory knowledge base ingestion + retrieval
        │   ├── routes/        ← FastAPI endpoints
        │   ├── db.py
        │   └── main.py
        ├── tests/
        ├── pyproject.toml
        └── .env.example
```

This is a monorepo by folder, not by tooling — there's no Turborepo/Nx layer for v1. Two independent apps in one git repo is enough; add a monorepo tool later only if shared code between them justifies it.

## Backend setup (apps/api)

Use `uv` for Python dependency and environment management — it's the current standard, far faster than pip/venv, and handles both the virtualenv and lockfile.

```bash
cd apps/api
uv init
uv add "pydantic-ai>=1,<2"        # pin to stable v1 line — v2 is in beta, don't build a portfolio project on a beta
uv add fastapi uvicorn[standard]
uv add "pydantic>=2"
uv add asyncpg psycopg[binary]    # Postgres drivers
uv add pgvector                   # pgvector Python bindings
uv add python-dotenv
uv add boto3                      # S3 presigned URLs
# dev dependencies
uv add --dev pytest pytest-asyncio ruff
```

Notes:

- Pin Pydantic AI to the v1 line explicitly. A v2 beta exists as of June 2026 but the stable release is still v1 — don't pull a beta into a project you want to be able to demo reliably.
- `pydantic-ai` includes the Anthropic provider, so you don't need a separate Claude SDK install. Set `ANTHROPIC_API_KEY` in your environment.
- Python 3.11+ recommended (Pydantic AI requires 3.10+).

Run the dev server:

```bash
uv run uvicorn src.main:app --reload
```

## Frontend setup (apps/web)

Next.js 16 is the current stable line. `create-next-app` gives you Turbopack (default) and the now-stable React Compiler out of the box.

```bash
# from repo root
npx create-next-app@latest apps/web --typescript --tailwind --app --no-src-dir
cd apps/web
npm install @tanstack/react-query   # data fetching against the API
npm install react-dropzone          # file upload UI
```

Run the dev server:

```bash
npm run dev
```

Requires Node.js 20+ (Next.js 16 minimum).

## Environment variables

`apps/api/.env.example` (copy to `.env`, never commit `.env`):

```
ANTHROPIC_API_KEY=
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=
```

`apps/web/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000   # the FastAPI service
```

The frontend only ever needs the API URL. It must never hold the Anthropic key, database URL, or AWS credentials — those live exclusively in `apps/api`, per the hard boundary in `02-architecture.md`.

## .gitignore essentials

```
# Python
.venv/
__pycache__/
*.pyc
.env

# Node
node_modules/
.next/
.env.local

# OS
.DS_Store
```

## Postgres + pgvector

Provision Postgres on Railway or Fly.io, then enable the extension once:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Both providers offer this on their managed Postgres. Use the same database for relational data and the knowledge base embeddings — no separate vector store for this scale.

## First task after setup

Once both dev servers run and the database is reachable, you're at the start of Phase 0 in `05-build-phases.md`: a health-check endpoint, one trivial typed Pydantic AI agent, and a Next.js page that calls it. Don't build further than that until the round-trip works end to end.
