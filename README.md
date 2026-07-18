# tariffa

An AI agent pipeline that helps Nigerian freight forwarders and clearing agents prepare and
pre-check import documentation for chemical and industrial raw-material shipments. It extracts
structured data from invoices and packing lists, classifies goods against HS codes and applicable
regulators (NAFDAC, SON), flags compliance issues against real regulatory rules before they cause
port delays, and drafts a Form M prep sheet.

It does **not** submit anything to a government system — output is a draft the user or their broker
files through the official channel (NICIS / Trade Window).

> **Plays:** the product, career, and audience playbooks live in [`PLAYS.md`](PLAYS.md).
> In a Claude Code session here, run `/play product` (or `career` / `audience`).

## Repository structure

```
apps/
  web/   — Next.js frontend (thin client; never talks to Postgres, S3, or Claude directly)
  api/   — Python FastAPI backend (agent orchestration, database, file storage, all LLM calls)
docs/    — detailed specs (read before working on the matching area)
```

This is a monorepo by folder, not by tooling — two independent apps in one git repo.

## Getting started

### Backend (`apps/api`)

```bash
cd apps/api
uv sync                                  # install deps from pyproject.toml / uv.lock
cp .env.example .env                     # then fill in the values
uv run uvicorn src.main:app --reload     # http://localhost:8000
```

### Frontend (`apps/web`)

```bash
cd apps/web
pnpm install
pnpm dev                                 # http://localhost:3000
```

The frontend needs only `NEXT_PUBLIC_API_URL` (see `apps/web/.env.local`). It must never hold the
Anthropic key, database URL, or AWS credentials — those live exclusively in `apps/api`.

## Docs

See [`CLAUDE.md`](CLAUDE.md) for the docs index. Start with [`docs/07-repository-setup.md`](docs/07-repository-setup.md).
