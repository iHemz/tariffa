# Architecture

## Service split

A monorepo with two independently deployed services:

- **`apps/web`** — Next.js. Owns the upload UI, the review/edit screen, and the dashboard. It is a thin client: no business logic, no direct calls to Postgres, S3, or the Claude API.
- **`apps/api`** — Python, FastAPI, Pydantic AI. Owns every agent in the pipeline, the database, file storage orchestration, and all LLM calls.

A monorepo means one repository, not one runtime. Splitting the runtime this way isn't a compromise — it's the correct shape for this problem, and it's also the architecture decision most worth being able to explain clearly in an interview: "the frontend is a thin client, all orchestration lives in one place" is a real, defensible design choice.

## Why Python + Pydantic AI for the agent layer, not JavaScript

- Pydantic AI reached its v1 milestone in September 2025 with a commitment to no breaking changes until v2 — it's no longer experimental infrastructure.
- It's built by the same team as Pydantic and FastAPI, so it's a native fit for this stack specifically, not a bolt-on.
- Type-validated agent outputs catch errors at the boundary between pipeline stages, before a bad HS code or a hallucinated compliance claim can flow downstream silently. This matters more here than in most agent projects, because the cost of being wrong (a flagged or seized shipment) is real.
- It has native support for AG-UI (the Agent-User Interaction Protocol), which gives a standard path for streaming agent state directly into a React/Next.js frontend without hand-rolled serialization. This directly serves the review screen, where the user watches extraction and compliance results come in.
- The known tradeoff: its multi-agent orchestration is lighter than LangGraph or CrewAI for complex, cyclical workflows. This pipeline doesn't need that — it's a linear sequence (extract → classify → check → draft), which is exactly the case Pydantic AI is built for.

## Data and storage

- **Postgres + pgvector**, one database covering both relational data (shipment records, extracted fields, compliance flags) and the regulatory knowledge base embeddings. No separate vector database — it adds an operational dependency this project doesn't need yet.
- **S3** for uploaded documents. Uploads go directly from the browser to a presigned S3 URL — files should not be proxied through both `web` and `api`, since that's two unnecessary hops for something that can only get larger over time.

## Deployment

- **`apps/web`** → Vercel. Zero-config for Next.js, free tier comfortably covers a side project.
- **`apps/api`** + Postgres → Railway or Fly.io. Both provide managed Postgres with the pgvector extension available and push-to-deploy from the repo. This is a deliberate choice over raw AWS: this project doesn't need to re-prove AWS competence (that's already on the CV from production work) — it needs to prove a working multi-agent system shipped, and a PaaS gets there without DevOps overhead eating into the time that should go to the agents themselves.

## Hard boundary, repeated because it matters

`apps/web` never calls Postgres, S3, or the Claude API directly. Every one of those goes through `apps/api`. If a feature in the frontend seems to need direct database access, that's a sign the API needs a new endpoint, not an exception to this rule.
