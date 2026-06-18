# Structured Output Guide (Claude + Pydantic)

## Overview

This guide documents how tariffa generates **structured, typed output** from the LLM. Every agent-to-agent handoff in the pipeline is a validated Pydantic model — no raw dicts cross a boundary. We get that guarantee two ways, both built on Claude (Anthropic):

1. **Pydantic AI agents** — the primary path. An `Agent` is parameterised by an `output_type`; Pydantic AI handles the structured-output request and returns a validated instance.
2. **Direct `client.messages.parse()`** — for one-off extraction calls outside the agent framework, where you want the typed result without spinning up an `Agent`.

Both rely on Claude's structured-output feature, which constrains the response to a JSON Schema derived from your Pydantic model.

## The Pattern

### Define the contract as a Pydantic model

The schema *is* the contract. Define it once; the same model validates the LLM output and types every downstream consumer.

```python
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(description="Goods description as printed on the invoice")
    quantity: float = Field(description="Quantity (numeric, units in `unit` field)")
    unit: str = Field(description="Unit of measure, e.g. 'kg', 'drums', 'cartons'")
    unit_price: float = Field(description="Unit price in the invoice currency")


class ExtractionResult(BaseModel):
    supplier_name: str = Field(description="Supplier / exporter name")
    currency: str = Field(description="ISO 4217 currency code, e.g. 'USD'")
    line_items: list[LineItem] = Field(
        description="One entry per line on the invoice / packing list"
    )
```

### Path 1 — Pydantic AI agent (primary)

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

extraction_agent = Agent(
    AnthropicModel("claude-opus-4-8"),
    output_type=ExtractionResult,
    system_prompt=(
        "Extract structured data from the supplied invoice and packing list. "
        "Return every line item. Do not invent values that are not present."
    ),
)

result = await extraction_agent.run(invoice_text)
# result.output is a validated ExtractionResult instance
print(result.output.supplier_name)
```

### Path 2 — Direct `client.messages.parse()`

For a single extraction without the agent abstraction, use the SDK's `parse()` helper. It validates the response against your Pydantic model and gives you a typed instance back.

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": invoice_text}],
    output_format=ExtractionResult,
)

result = response.parsed_output  # validated ExtractionResult, or None on refusal
```

## How It Works

Claude's structured-output API constrains generation to a JSON Schema derived from your Pydantic model. The model is steered to produce output that matches the schema's shape — types, required fields, enums, and nesting — and the SDK parses and validates the result for you.

- **Shape is enforced server-side.** Types, `required`, `enum`, `const`, `anyOf`, nested objects, and string formats (`date`, `email`, `uri`, etc.) are honoured during generation.
- **Numeric and length constraints are not.** `minLength`/`maxLength`/`minItems`/`maxItems`/`minimum`/`maximum` are not enforced at generation time. The SDK strips them from the schema it sends and re-applies them client-side after parsing. They still validate — just as a post-parse check, not a generation guarantee. (See [ai-provider-configuration.md](./ai-provider-configuration.md) → Structured Output Schema Constraints.)

The practical consequence: **put constraints in `Field(description=...)`**, not only in validators. The description steers generation; the validator catches anything that slips through.

## Why This Pattern

1. **One schema, many guarantees** — the Pydantic model is the typed contract between pipeline stages, the validation layer, and the source of TypeScript types on the frontend (generated from the same schemas).
2. **No raw dicts across boundaries** — a non-negotiable in this codebase. Structured output is how we hold that line.
3. **Refusal-safe** — `parsed_output` is `None` (and `stop_reason` is `"refusal"`) when the model declines; the pipeline treats that as a failed stage rather than crashing on a malformed dict.
4. **Centralised** — extraction, classification, compliance, and Form M drafting all use the same two paths; there is no bespoke JSON-parsing code per stage.

## Common Pitfalls to Avoid

### Handle `max_tokens` truncation

**Symptom:** the parsed result is missing trailing fields, or parsing fails outright, and `stop_reason` is `"max_tokens"`.

**Cause:** the model hit the output cap before completing the JSON.

**Fix:** raise `max_tokens` for stages that emit large structured output. Extraction over a long, multi-page packing list is the usual culprit.

```python
# Extraction can be large — give it room
response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=16000,         # raise for long documents; stream above ~16K
    messages=[{"role": "user", "content": invoice_text}],
    output_format=ExtractionResult,
)
```

For very large outputs (above ~16K), stream the request to avoid SDK HTTP timeouts.

### Don't put hard constraints only in the schema and expect the model to obey them

```python
# Weak — the bound is invisible to the model during generation
class Bad(BaseModel):
    hs_code: str = Field(min_length=8, max_length=10)
```

```python
# Strong — the bound is in the description (steers generation)
#          AND in the constraint (validates after parse)
class Good(BaseModel):
    hs_code: str = Field(
        min_length=8,
        max_length=10,
        description="HS code, 8-10 digits, no separators (e.g. '28289010')",
    )
```

### Don't hand-roll JSON extraction

```python
# Wrong — never scrape JSON out of a free-text response
text = response.content[0].text
data = json.loads(text.split("```json")[1])  # fragile
```

```python
# Right — let the SDK parse and validate against your model
result = response.parsed_output
```

### Always check for refusal before reading the result

```python
if response.parsed_output is None:
    # stop_reason == "refusal" — treat as a failed stage, log, surface to the user
    handle_refusal(response)
else:
    use(response.parsed_output)
```

## Schema Definition Tips

When designing a Pydantic output model for a pipeline stage:

- **Describe every field.** The model reads descriptions to decide what to put where. Treat them as instructions, not documentation.
- **Encode bounds in descriptions**, with Pydantic constraints as the validation backstop.
- **Use enums for fixed value sets** (e.g. regulator names, document types) — these *are* enforced server-side.
- **Keep optional fields optional** (`field: str | None = None`) rather than forcing the model to invent a value.
- **Prefer flat-ish structures** where the data allows — deeply nested schemas are harder for the model to fill reliably.

## Testing Checklist

When implementing or changing a structured-output stage:

- [ ] Output is defined as a Pydantic model with a description on every field
- [ ] Constraints appear in both `Field(description=...)` and as Pydantic validators
- [ ] Using a Pydantic AI `Agent` (`output_type=...`) or `client.messages.parse()` — not manual JSON parsing
- [ ] `max_tokens` is sized for the largest realistic document; streaming above ~16K
- [ ] Refusal (`parsed_output is None`) is handled as a failed stage
- [ ] Tested against real documents, not just synthetic fixtures

## Related Files

- `app/ai/schemas.py` — the Pydantic output contracts for every pipeline stage
- `app/ai/agents.py` — Pydantic AI agent builders (extraction, classification, compliance, Form M)
- `app/ai/config.py` — provider/model resolution
- [ai-provider-configuration.md](./ai-provider-configuration.md) — provider configuration and the structured-output constraint table
- `docs/04-data-models.md` — the canonical typed contracts between pipeline stages
