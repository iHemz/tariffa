---
paths:
  - "apps/api/**/agents/**/*.py"
  - "apps/api/**/*agent*.py"
  - "apps/api/**/pipeline/**/*.py"
  - ".claude/agents/**/*.md"
---

# AI-Human Engineering Stack — Mandatory Design Checklist

Before building or modifying any agent in the tariffa pipeline (extraction, classification, compliance, Form M drafting), evaluate all six layers of the AI-Human Engineering Stack. Each layer depends on all layers beneath it. An agent missing a layer will produce brittle, unreliable output — and in this domain, an unreliable compliance flag is worse than no flag.

---

## The Six Layers (Bottom to Top)

### 1. Prompt Engineering — "What to do"

The base instruction set. What does the agent do when invoked?

- Clear task definition with positive directives
- Structured output schemas (Pydantic models — every agent returns a typed model, never a raw dict)
- Tool definitions and usage patterns (Pydantic AI tools)
- Few-shot examples where appropriate (behind tools, not inlined into the system prompt)

### 2. Context Engineering — "What to know while doing"

What information does the agent need access to while executing?

- What data is injected into the prompt (extracted invoice fields, prior agent outputs, the document under review)?
- What tools provide on-demand context (RAG over the regulatory knowledge base, HS-code lookups)?
- What is the agent's context window budget and how is it managed?
- Is context fresh, or could it be stale (e.g. an outdated regulatory rule)? How is staleness handled?

The compliance agent in particular must be grounded in **retrieved regulatory text**, never the model's own unverified knowledge of Nigerian customs law.

### 3. Intent Engineering — "What to want while doing"

What is the agent optimizing for? What does "good" look like?

- Define the success criteria explicitly (not just "check compliance" — e.g. "every flag cites the rule it came from")
- Quality rubrics and self-check checklists
- Priority ordering when goals conflict (e.g. completeness of flags vs. avoiding false positives that erode trust)
- Skill routing — which capabilities activate for which document types or regulators?

### 4. Judgment Engineering — "What to doubt while doing"

Where should the agent be uncertain, and how should it handle uncertainty?

- Escalation rules — when does the agent surface "needs human review" vs. proceed autonomously? (This tool drafts and pre-checks; it never auto-submits.)
- Confidence thresholds for an HS-code classification vs. flagging it for the user to confirm
- Error recovery — what does the agent do when a tool call fails, retrieval returns nothing, or output fails Pydantic validation?
- Interrogation points — where does a downstream agent or check review an upstream agent's output?

### 5. Coherence Engineering — "What to become while doing"

How does the agent maintain consistent identity and behavior across turns?

- Agent identity and persona (a careful customs-prep assistant, not a chatbot)
- Behavioral consistency across a multi-document shipment
- Memory and state management between pipeline stages
- How does the agent avoid drift from its design intent over a long extraction?

### 6. Evaluation Engineering — "How to know while doing" (The Loop)

How do we measure whether the agent is working? Each layer is evaluated in a loop.

- What evals exist for this agent? (pytest cases on pure prompt builders and parsers, golden-set documents with known-correct extractions/classifications)
- How do we detect regression? (Test names as architectural invariants)
- What metrics indicate the agent is performing well or poorly (extraction accuracy, classification precision, flag recall)?
- How does eval feedback flow back into prompt/context/intent improvements?

---

## Harness Engineering — "Where and how to do"

The infrastructure that sets up and runs the agent. I configure this initially and adjust as needed.

- Orchestrator wiring (pipeline stage ordering, execution flow, failure policy)
- Model selection and fallback strategy (Claude API)
- Rate limiting, timeout, and retry configuration
- Background execution and monitoring (FastAPI background tasks)

---

## How to Apply This

When creating a new agent or significantly modifying an existing one:

1. **Document each layer** in the agent's design (a spec in `/docs/`, an ADR, or inline comments)
2. **Identify gaps** — a missing layer is a conscious decision, not an oversight. If a layer is intentionally skipped, note why.
3. **Build bottom-up** — Prompt and Context first, then Intent and Judgment, then Coherence and Eval
4. **Eval closes the loop** — every agent should have at least one eval that validates its output quality

This checklist is a design tool, not a bureaucratic gate. A simple single-pass extraction agent may intentionally skip Coherence. The compliance agent needs all six. The point is to make the decision consciously.
