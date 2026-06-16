# Build phases

Sequenced to front-load the riskiest unknowns and the things that take real-world time to resolve, not just coding time. Budgets assume part-time, evenings/weekends pace.

## Phase 0 — Skeleton (~1 week)

Prove the full stack talks to itself before any real logic exists.

- FastAPI health-check endpoint.
- One Pydantic AI agent that calls Claude with a typed output and returns it — nothing more.
- Next.js page that hits that endpoint.
- Postgres + pgvector provisioned (Railway or Fly.io), a minimal shipments table.

The point of this phase is de-risking infrastructure and Python tooling (environment, dependency management, deployment) in isolation, before debugging new infra and new business logic at the same time.

## Phase 1 — Extraction agent (~2-3 weeks)

Single document type only: a commercial invoice for a chemical/raw-material shipment.

- Define the `InvoiceExtraction` / `LineItem` schemas.
- Build the extraction agent against real or realistic sample invoices.
- The hard part isn't the code, it's sourcing test documents with enough formatting variety to actually test extraction quality. Treat this as its own task.

## Phase 2 — Classification + compliance agents (~3-4 weeks, the real time sink)

This is the core IP, and the regulatory research is the bottleneck, not the agent code.

- Gather actual source material: NCS tariff chapters relevant to chemicals (28, 29, 38), NAFDAC import requirements for regulated chemical categories, SON/SONCAP requirements where applicable. See `06-regulatory-knowledge-base.md`.
- Build the classification agent (description → HS code candidate + applicable regulator).
- Build the compliance agent, grounded against the knowledge base, with citations on every flag.

Don't start the agent code until there's at least a first pass of real regulatory source material to ground it against — an ungrounded compliance agent is worse than none.

## Phase 3 — Form-drafting + review UI (~2 weeks)

This is the part closest to existing strengths, so it should move fastest.

- Form M prep sheet generation from validated data.
- Review screen: document viewer, editable extracted fields, compliance flags, export button.

## Phase 4 — Polish and validation (~1-2 weeks, ongoing)

- 2-3 polished example shipments to demo with.
- A short recorded walkthrough.
- Get one or two real freight forwarders to actually try it — this is what turns "a project I built" into "a product people want," which is the actual point of doing this.

Total: roughly 10-12 weeks part-time. If a phase is taking meaningfully longer than budgeted, that's useful information about where the real difficulty lives — don't treat the estimate as a deadline to force.
