# Tariffa

An AI agent pipeline that prepares and pre-checks Nigerian import documentation for chemical and
industrial raw-material shipments. Upload a commercial invoice and packing list. Tariffa extracts
the structured fields, classifies each line item against an HS code and the regulator it falls
under (NAFDAC, SON, or none), checks the shipment against retrieved regulatory text, and drafts a
Form M prep sheet from the validated data.

It submits nothing. Filing through NICIS or Trade Window needs accreditation this project does
not have and should not pretend to have. The output is a draft that the user or their licensed
broker files through the official channel.

**Status: in progress.** The extraction agent is built and verified on a synthetic invoice.
Classification, compliance (RAG-grounded) and Form M drafting are next. See [`TODO.md`](TODO.md).

## The problem

A Nigerian shipment sits at port for weeks over a missing NAFDAC certificate, a wrong HS code
chapter, or an inconsistency between the invoice and the Form M. That is expensive in money and
in time, and it is caught manually today, after submission, if at all.

The compounding is what makes freight forwarders the right first user. They process shipments
repeatedly, so catching one class of error before submission pays back on every shipment after it.

## The idea worth stealing

The tempting version of this tool answers customs questions from the model's own memory of
Nigerian regulation. That version is worse than no tool at all, because a confident wrong
compliance claim is exactly the thing a clearing agent cannot afford to trust.

So the compliance agent is RAG-grounded by rule, not by preference. Every flag it raises carries
a citation to the specific retrieved rule that triggered it. If it cannot point at the rule, it
does not raise the flag.

The same instinct runs one stage earlier. When the classification agent is unsure which HS code
or regulator applies, it says so and marks the confidence. A flagged uncertainty is more useful
to a clearing agent than a confident guess, because the uncertainty is something they can go and
resolve in two minutes with knowledge the model does not have.

## How it works

```
upload (invoice + packing list, PDF or image)
  -> extraction agent   : structured fields (seller, buyer, line items, currency, incoterm, values)
  -> classification agent: HS code candidate + confidence + applicable regulator, per line item
  -> compliance agent   : RAG against the regulatory knowledge base, flags with rule citations
  -> review screen      : the user edits and approves the fields
  -> form-drafting agent: Form M prep sheet (PDF) from the approved data
```

Four agents, one linear pass. Every handoff between them is a validated Pydantic model, never a
raw dict.

Three decisions carry most of the weight:

**No separate OCR step.** Claude reads PDFs and images natively, so the document goes straight to
a call with a structured output schema. A dedicated OCR pipeline is a real option later, but only
if extraction quality on real documents proves it is needed. Building it first would have been
work spent before the evidence existed.

**One vertical, deliberately.** Chemicals and industrial raw materials, roughly HS chapters 28,
29 and 38. That is what keeps the regulatory knowledge base tractable enough to be correct.
Electronics and SON-regulated building materials are additions to a proven pipeline, not a wider
v1.

**The pipeline stays linear.** No negotiation between agents, no revision loops, no agent
critiquing another's output. That complexity is not earned yet, and it works against Pydantic
AI's actual strength, which is typed and predictable single-pass agents.

## The riskiest part

Extraction, not compliance. Extraction quality varies a lot with document formatting, and every
later stage inherits whatever it gets wrong. Anyone building this should budget real testing time
against a handful of genuinely messy invoices before assuming the stage works.

Stating that here rather than discovering it in a demo is the point.

## Running it

Prerequisites: Node, pnpm, uv, Python 3.12, and an Anthropic API key.

```bash
# Backend, on :8000
cd apps/api
uv sync
cp .env.example .env                     # fill in the values
uv run uvicorn src.main:app --reload

# Frontend, on :3000
cd apps/web
pnpm install
pnpm dev
```

The frontend needs only `NEXT_PUBLIC_API_URL`. It must never hold the Anthropic key, the database
URL, or the AWS credentials. Those live in `apps/api` and nowhere else.

## Repository structure

```
apps/
  web/   Next.js frontend. A thin client: it never talks to Postgres, S3, or Claude directly.
  api/   FastAPI backend. Agent orchestration, database, file storage, every LLM call.
docs/    Specs. Read the matching one before working on an area.
```

A monorepo by folder, not by tooling. Two independent apps in one git repo.

## Docs

`CLAUDE.md` holds the index. Start with `docs/07-repository-setup.md`. The product boundary is in
`docs/01-product-vision.md`, the agent contracts in `docs/03-agent-pipeline.md`, and the schemas
in `docs/04-data-models.md`.

## What would make this real

Not "the code runs." The bar is a working freight forwarder, shown two or three realistic
shipments through the full pipeline, saying it would have caught something or saved them time.
Everything before that is a demo.
