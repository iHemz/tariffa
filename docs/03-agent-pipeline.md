# Agent pipeline

Four agents, run in a linear sequence. Each handoff between them is a validated Pydantic model — see `04-data-models.md` for the actual schemas. No agent should ever pass a raw dict to the next one.

## 1. Extraction agent

**Input:** uploaded invoice and packing list (PDF or image).
**Output:** `InvoiceExtraction` (see data models doc).
**Responsibility:** pull structured fields — seller, buyer, line items, currency, incoterm, declared values — out of the source documents.

Note: Claude can read PDFs and images natively. Prefer sending the document directly to a Claude call with a structured output schema over building a separate OCR step — it's simpler and likely more accurate for this use case, and a dedicated OCR pipeline can be added later only if extraction quality on real documents proves it's needed.

**Known risk:** extraction quality varies a lot with document formatting. The riskiest unknown in the whole project is here, not in the later agents — budget real testing time against a handful of realistic sample invoices before assuming this stage works.

## 2. Classification agent

**Input:** the line items from `InvoiceExtraction`.
**Output:** `ClassificationResult` per line item — HS code candidate, confidence, and which regulator applies (NAFDAC, SON, or none).
**Responsibility:** map a product description to the correct HS code chapter and determine regulatory exposure. Start narrow: the chemical-relevant chapters (roughly 28, 29, 38) rather than the full tariff book.

**Known risk:** ambiguous product descriptions. When confidence is low, the agent should say so explicitly rather than guess — a flagged uncertainty is far more useful to a clearing agent than a confident wrong answer.

## 3. Compliance agent

**Input:** `InvoiceExtraction` + `ClassificationResult`, plus retrieval against the regulatory knowledge base (see `06-regulatory-knowledge-base.md`).
**Output:** `ComplianceReport` — a list of `ComplianceFlag` items, each with a citation to the specific rule that triggered it.
**Responsibility:** check the shipment against real, retrieved regulatory text — missing certificates, undervaluation red flags, missing NAFDAC/SON registration where required.

**Non-negotiable:** this agent must be RAG-grounded. It should never answer from the model's own unverified memory of Nigerian customs law — that's the single biggest credibility risk in the entire project, since a wrong compliance claim is worse than no tool at all.

## 4. Form-drafting agent

**Input:** the validated, user-approved data after review.
**Output:** a Form M prep sheet (PDF), populated from the validated fields.
**Responsibility:** produce a document the user or their broker can use to actually file — not a submission, a draft. See the scope boundary in `01-product-vision.md`.

## Orchestration note

Keep this pipeline linear. There's no need for agents to negotiate, loop, or revise each other's output for v1 — that complexity isn't earned yet, and it plays against Pydantic AI's actual strength (typed, predictable single-pass agents) rather than with it.
