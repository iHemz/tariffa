# Data models

Draft schemas for the typed contracts between pipeline stages. These are starting points to refine once real sample documents are in hand, not final.

```python
from pydantic import BaseModel
from datetime import date
from enum import Enum

class Regulator(str, Enum):
    NAFDAC = "NAFDAC"
    SON = "SON"
    NONE = "NONE"

class LineItem(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    total_value: float
    country_of_origin: str

class InvoiceExtraction(BaseModel):
    seller: str
    buyer: str
    invoice_date: date
    currency: str
    incoterm: str
    line_items: list[LineItem]

class ClassificationResult(BaseModel):
    line_item_index: int
    hs_code_candidate: str
    confidence: float  # 0-1, surface low-confidence results to the user rather than guessing
    applicable_regulator: Regulator
    reasoning: str  # short explanation, helps the human reviewer trust or override the call

class ComplianceFlag(BaseModel):
    severity: str  # "blocking" | "warning" | "info"
    message: str
    cited_rule: str  # which specific regulation/source this flag is grounded in
    related_line_item_index: int | None = None

class ComplianceReport(BaseModel):
    shipment_id: str
    flags: list[ComplianceFlag]
    overall_status: str  # "clear" | "needs_attention" | "blocked"

class FormDraft(BaseModel):
    shipment_id: str
    form_type: str  # "Form M prep sheet"
    pdf_url: str
    generated_at: date
```

## Notes

- `confidence` and `reasoning` fields on `ClassificationResult` aren't decoration — they're what lets the review UI distinguish "trust this" from "check this," which is the actual value the human-in-the-loop step provides.
- `cited_rule` on `ComplianceFlag` is non-negotiable. A flag without a citation back to source text is not meaningfully different from a guess, and undermines the entire premise of the compliance agent.
- These models are the contract enforced at every pipeline boundary — validate against them explicitly rather than trusting an LLM call's raw output.
