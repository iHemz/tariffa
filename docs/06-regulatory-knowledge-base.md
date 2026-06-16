# Regulatory knowledge base

This is the research work behind the compliance agent, and it's genuinely the slowest part of the project — budget real time for it rather than treating it as a quick data-loading step.

## What to gather

- **Nigeria Customs Service tariff book**, focused on the chapters relevant to chemicals and industrial raw materials — likely chapters 28 (inorganic chemicals), 29 (organic chemicals), and 38 (miscellaneous chemical products). Don't try to ingest the full tariff book for v1.
- **NAFDAC import guidelines** for chemical categories that require registration (this varies by use case — chemicals destined for food, pharmaceutical, or cosmetic applications fall under NAFDAC; general industrial chemicals often don't).
- **SON / SONCAP requirements** where applicable to the product category.

## Sourcing discipline

Use primary, official sources only — the actual NCS, NAFDAC, and SON publications — not third-party summaries or blog posts about them. A compliance agent grounded in someone else's possibly-outdated paraphrase is barely better than one grounded in nothing. Record where each document came from and when it was retrieved, since regulations change and a knowledge base needs to be revisited, not treated as permanent.

## Structuring for retrieval

- Chunk by individual rule or requirement, not by raw page — a chunk should be small enough that retrieving it gives the compliance agent one coherent, checkable fact.
- Store metadata alongside each embedding: source document, section/chapter reference, and date retrieved. This is what makes the `cited_rule` field on `ComplianceFlag` (see `04-data-models.md`) meaningful rather than decorative.
- Keep the embeddings in the same Postgres instance via pgvector — no separate vector database for this scale.

## Why this matters more than it might seem

The entire credibility of the compliance agent rests on this knowledge base being accurate and traceable. A flag with a real citation is a product. A flag the model invented from general knowledge of "how customs usually works" is a liability — it's the difference between a tool a freight forwarder would actually trust and one they'd quietly stop using after the first wrong flag.
