# AI Provider and Model Configuration

## Overview

This document explains how the LLM provider and model are configured in tariffa's `apps/api` backend. The agent pipeline runs on **Claude (Anthropic) via Pydantic AI**. Claude is the primary — and, for v1, the only — provider. The configuration is structured so a second provider could be added later without rewriting call sites, but everything in the pipeline assumes Claude today.

All LLM calls live in `apps/api`. The Next.js frontend never talks to the Claude API directly — it calls our FastAPI endpoints, which own orchestration, model selection, and the API key.

## Precedence Order

Each agent run resolves its provider and model from the first source that supplies one (highest to lowest):

1. **Explicit call arguments** — passed directly when invoking an agent (e.g. a one-off override in a script or test)
2. **Operation-specific defaults** — the configured default for that pipeline stage (e.g. `EXTRACTION`, `CLASSIFICATION`)
3. **Global defaults** — the fallback in `app/ai/config.py`

There is no query-string or request-body override exposed to the frontend. Model selection is a backend concern; the thin client cannot pick a model.

## Operation-Specific Defaults

Each pipeline stage has its own default model. Most stages run on Claude Opus 4.8; high-volume, low-complexity stages can run on a cheaper model. Defaults live in `app/ai/config.py`:

```python
from app.ai.config import AIProvider, ModelDefaults

AI_OPERATION_DEFAULTS: dict[str, ModelDefaults] = {
    # Extract structured data from invoices / packing lists
    "EXTRACTION": ModelDefaults(
        provider=AIProvider.ANTHROPIC,
        model="claude-opus-4-8",
    ),
    # Classify goods against HS codes and applicable regulators
    "CLASSIFICATION": ModelDefaults(
        provider=AIProvider.ANTHROPIC,
        model="claude-opus-4-8",
    ),
    # Flag compliance issues against retrieved regulatory text (RAG)
    "COMPLIANCE_CHECK": ModelDefaults(
        provider=AIProvider.ANTHROPIC,
        model="claude-opus-4-8",
    ),
    # Draft the Form M prep sheet from validated pipeline output
    "FORM_M_DRAFT": ModelDefaults(
        provider=AIProvider.ANTHROPIC,
        model="claude-opus-4-8",
    ),
}
```

### Modifying Operation Defaults

To change the default model for a stage, edit `AI_OPERATION_DEFAULTS` in `app/ai/config.py`:

```python
# Example: run extraction on a cheaper, faster model for high-volume batches
"EXTRACTION": ModelDefaults(
    provider=AIProvider.ANTHROPIC,
    model="claude-haiku-4-5",
),
```

When you change a default, document *why* — extraction accuracy on dense scanned invoices is sensitive to model choice, and the compliance stage must stay on a strong model because its output drives go/no-go decisions for the user.

## Wiring Claude into Pydantic AI

Each agent is a `pydantic_ai.Agent` parameterised by a typed output model. The model and provider come from the resolver, not hard-coded at the call site.

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from app.ai.config import resolve_model
from app.ai.schemas import ExtractionResult  # typed Pydantic output contract


def build_extraction_agent() -> Agent[None, ExtractionResult]:
    spec = resolve_model("EXTRACTION")  # provider + model id
    model = AnthropicModel(spec.model)  # reads ANTHROPIC_API_KEY from env
    return Agent(
        model,
        output_type=ExtractionResult,
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
    )
```

`resolve_model` applies the precedence order above and returns a small `ModelSpec` (provider + model id). Keeping resolution in one place means there is a single source of truth for which model each stage uses.

### Defaults and Model Choice

Default to **Claude Opus 4.8** (`claude-opus-4-8`) for every stage unless you have a measured reason to do otherwise. It is the most capable Opus-tier model and the right default for extraction, classification, and the regulatory reasoning the compliance stage depends on.

| Model | Model ID | Use it for |
| --- | --- | --- |
| Claude Opus 4.8 | `claude-opus-4-8` | Default — extraction, classification, compliance, Form M drafting |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | High-volume production batches where Opus cost is a concern |
| Claude Haiku 4.5 | `claude-haiku-4-5` | Simple, speed-critical sub-steps (e.g. cheap pre-classification triage) |

Use only the exact model ID strings above — they are complete as written. Do not append date suffixes.

## Adapting Defaults for Cost or Latency

Because resolution is centralised, switching a stage to a cheaper model is a one-line config change with no edits at the call sites. Set per-stage defaults in `AI_OPERATION_DEFAULTS`; override per-run via explicit call arguments only in tests or scripts.

```python
from app.ai.agents import build_extraction_agent

# Uses the EXTRACTION default (Claude Opus 4.8)
agent = build_extraction_agent()

# One-off override for a benchmark run
agent = build_extraction_agent(model="claude-sonnet-4-6")
```

## Benefits

1. **Single source of truth** — all model selection logic lives in `app/ai/config.py`.
2. **Per-stage optimisation** — each pipeline stage can run on the model best suited to it.
3. **Typed contracts** — every agent returns a validated Pydantic model, not a raw dict (see `docs/04-data-models.md`).
4. **Cheap experimentation** — change a model in one place to A/B a stage without touching call sites.
5. **No frontend coupling** — the thin client never sees or chooses a model.

---

## Structured Output Schema Constraints

The pipeline relies on Claude's structured output: each agent returns a typed Pydantic model, validated before it crosses a pipeline boundary. When Pydantic models are converted to JSON Schema for the structured-output API, a few schema features are **not** enforced server-side.

### What Claude's structured output does NOT enforce

Claude's structured output guarantees the response matches your schema's *shape* (types, required fields, enums, nesting), but does **not** enforce numeric or length *constraints* at the API level:

| Pydantic constraint | JSON Schema property | Enforced by the API? |
| --- | --- | --- |
| `min_length` on `str` | `minLength` | No |
| `max_length` on `str` | `maxLength` | No |
| `min_length` on `list` | `minItems` | No |
| `max_length` on `list` | `maxItems` | No |
| `ge` / `gt` on numbers | `minimum` | No |
| `le` / `lt` on numbers | `maximum` | No |

The Anthropic Python SDK strips these unsupported constraints from the schema it sends and re-applies them **client-side** when you use `client.messages.parse()` with a Pydantic model — so they still validate, but as a post-parse check, not a generation-time guarantee.

### Communicate constraints in field descriptions

Because the model isn't constrained server-side, the reliable way to steer it is the field `description`. Put the bound in plain language so the model produces compliant output in the first place, and keep the Pydantic constraint as the validation backstop:

```python
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    hs_code: str = Field(
        description="HS code, 8-10 digits, no separators (e.g. '28289010')"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Classification confidence between 0.0 and 1.0",
    )
    candidate_codes: list[str] = Field(
        description="1-5 alternative HS codes, most likely first",
    )
    regulators: list[str] = Field(
        description="Applicable regulators, e.g. ['NAFDAC'] or ['SON'] or both",
    )
```

The `ge`/`le` constraints above still validate client-side after parsing; the descriptions are what actually keep the model on-spec during generation.

See [gemini-structured-output-guide.md](./gemini-structured-output-guide.md) for the full structured-output pattern used across the pipeline (Pydantic AI agents and `client.messages.parse()`).
