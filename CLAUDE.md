# CLAUDE.md

This file gives Claude Code context on this repository. Keep this file short — detailed specs live in `docs/`, this file only navigates to them. Read the relevant doc before working on that part of the system; don't assume content from memory of a previous session.

## Project summary

An AI agent pipeline that helps Nigerian freight forwarders and clearing agents prepare and pre-check import documentation for chemical and industrial raw-material shipments. It extracts structured data from invoices and packing lists, classifies goods against HS codes and applicable regulators (NAFDAC, SON), flags compliance issues against real regulatory rules before they cause port delays, and drafts a Form M prep sheet. It does **not** submit anything to a government system — output is a draft the user or their broker files through the official channel (NICIS / Trade Window).

v1 user: freight forwarders / clearing agents (the wedge). SME importers are a self-serve layer planned for after v1 is proven.

## Repository structure

```
apps/
  web/   — Next.js frontend. Upload UI, review screen, dashboard. Never talks to Postgres, S3, or the Claude API directly.
  api/   — Python FastAPI backend. Owns all agent orchestration (Pydantic AI), the database, file storage, and all LLM calls.
docs/    — detailed specs, read before working on the matching area
```

## Docs index

| File | Read this when you're working on... |
|---|---|
| `docs/01-product-vision.md` | Anything about scope, target user, or what "done" means for v1 |
| `docs/02-architecture.md` | Infra, deployment, service boundaries, why Next.js + FastAPI + Pydantic AI |
| `docs/03-agent-pipeline.md` | Any of the four agents — their responsibility, inputs, outputs, known edge cases |
| `docs/04-data-models.md` | Pydantic schemas — the actual typed contracts between pipeline stages |
| `docs/05-build-phases.md` | Sequencing — what to build now vs. later, and why |
| `docs/06-regulatory-knowledge-base.md` | The RAG knowledge base — what regulatory sources to gather and how to structure them |
| `docs/07-repository-setup.md` | Folder structure, package installation, setup commands — read this first when scaffolding the repo |

## Non-negotiables

- The frontend is a thin client. All business logic, validation, and AI orchestration lives in `apps/api`.
- Every agent-to-agent handoff is a typed Pydantic model, validated before it's passed downstream. No raw dicts crossing a pipeline boundary.
- The compliance agent must be grounded in retrieved regulatory text (RAG), never relying on the model's own unverified knowledge of Nigerian customs law.
- This tool drafts and pre-checks. It never claims to submit to NICIS, Trade Window, or any government system on the user's behalf.
- Large file uploads go browser → S3 directly via a presigned URL. Don't proxy files through both `web` and `api`.
