# Validation Patterns

Guide to the Pydantic validation patterns used throughout tariffa's `apps/api` backend.

All business validation lives in `apps/api`. The frontend (`apps/web`) is a thin client: it uses TypeScript types for shape and editor support, but it is never the validation authority. Every value is validated again at the API boundary on the backend — the client cannot be trusted to have done it.

## Table of Contents

- [Pydantic Model Patterns](#pydantic-model-patterns)
- [Custom Validators](#custom-validators)
- [Error Message Standards](#error-message-standards)
- [Request Validation in FastAPI](#request-validation-in-fastapi)
- [Pipeline-Boundary Validation](#pipeline-boundary-validation)
- [Frontend Types](#frontend-types)
- [Best Practices](#best-practices)

---

## Pydantic Model Patterns

### Basic Model Definition

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Supplier(BaseModel):
    # Required field with a descriptive constraint message
    name: str = Field(min_length=1, description="Supplier name (required)")

    # Email with format validation
    email: EmailStr = Field(description="Supplier contact email")

    # Optional field
    description: str | None = None

    # Field with a default
    is_active: bool = True
```

### Enum Patterns

Define a canonical `Enum` once and reuse it everywhere — in models, in the database layer, and as the source of the frontend's generated union type. Never redefine the same set of literal values in two places.

```python
from enum import Enum
from pydantic import BaseModel


class Regulator(str, Enum):
    NAFDAC = "NAFDAC"
    SON = "SON"


class ShipmentStatus(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    CLASSIFYING = "classifying"
    CHECKING_COMPLIANCE = "checking_compliance"
    DRAFTED = "drafted"
    FAILED = "failed"


class Classification(BaseModel):
    regulators: list[Regulator]      # reuse the canonical enum
    status: ShipmentStatus
```

Inheriting from `str` (`class Regulator(str, Enum)`) makes the enum JSON-serialisable and keeps the wire value equal to the member value.

### Date Fields

Pydantic coerces ISO 8601 strings to `datetime` automatically — no special handling needed.

```python
from datetime import datetime
from pydantic import BaseModel


class Shipment(BaseModel):
    created_at: datetime                     # parsed from an ISO string
    scheduled_at: datetime | None = None     # optional
```

### Nested Models

```python
class Address(BaseModel):
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    country: str = Field(min_length=1)


class Importer(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    address: Address | None = None
```

### Lists

```python
class LineItem(BaseModel):
    description: str
    quantity: float = Field(gt=0)


class PackingList(BaseModel):
    tags: list[str] = Field(default_factory=list)
    items: list[LineItem]
```

---

## Custom Validators

### Field Validators

Use `field_validator` for single-field rules (formats, normalisation):

```python
import re
from pydantic import BaseModel, field_validator


class Classification(BaseModel):
    hs_code: str

    @field_validator("hs_code")
    @classmethod
    def hs_code_must_be_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{8,10}", v):
            raise ValueError("HS code must be 8-10 digits with no separators")
        return v
```

### Constrained Numbers

Prefer `Field` constraints over hand-written validators for ranges:

```python
class Classification(BaseModel):
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence between 0 and 1")


class LineItem(BaseModel):
    quantity: float = Field(gt=0, description="Must be positive")
```

### Cross-Field Validation

Use `model_validator(mode="after")` when a rule spans more than one field:

```python
from pydantic import BaseModel, model_validator


class ComplianceFlag(BaseModel):
    severity: str
    blocking: bool

    @model_validator(mode="after")
    def critical_flags_must_block(self) -> "ComplianceFlag":
        if self.severity == "critical" and not self.blocking:
            raise ValueError("Critical compliance flags must be blocking")
        return self
```

---

## Error Message Standards

### Descriptive Messages

```python
# Weak — opaque on failure
name: str = Field(min_length=1)

# Strong — tells the caller what's wrong
name: str = Field(min_length=1, description="Name is required and cannot be empty")
```

### Field-Specific Messages

```python
class Importer(BaseModel):
    name: str = Field(min_length=1, description="Importer name is required")
    email: EmailStr = Field(description="Provide a valid contact email")
```

FastAPI surfaces Pydantic `ValidationError`s as structured 422 responses automatically — each error carries the field location (`loc`), a message (`msg`), and a type. Keep messages specific so the response is actionable.

---

## Request Validation in FastAPI

FastAPI validates request bodies against the declared Pydantic model before your handler runs. A malformed body never reaches your code — it's rejected with a 422 and a structured error.

### Create / Update Models

Split the persisted model from the request models. The create model omits server-owned fields (`id`, `user_id`, timestamps); the update model makes everything optional for partial updates.

```python
from pydantic import BaseModel


class ShipmentFields(BaseModel):
    """Shared field definitions."""
    reference: str
    importer_name: str
    notes: str | None = None


class CreateShipment(ShipmentFields):
    """Request body for creating a shipment.

    `user_id`, `id`, and timestamps are set by the server, not the client.
    """


class UpdateShipment(BaseModel):
    """All fields optional for partial updates."""
    reference: str | None = None
    importer_name: str | None = None
    notes: str | None = None


class ShipmentResponse(ShipmentFields):
    id: str
    user_id: str
    created_at: datetime
```

### Using Them in Routes

```python
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/shipments", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    payload: CreateShipment,              # validated before this runs
    user_id: str = Depends(current_user),
):
    return await shipment_service.create(payload, user_id=user_id)


@router.patch("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: str,
    payload: UpdateShipment,              # partial; only provided fields are set
    user_id: str = Depends(current_user),
):
    return await shipment_service.update(shipment_id, payload, user_id=user_id)
```

`response_model` validates and filters the *outgoing* response too — fields not on the response model never leak to the client.

---

## Pipeline-Boundary Validation

This is the non-negotiable one. **Every agent-to-agent handoff in the pipeline is a typed Pydantic model, validated before it's passed downstream. No raw dicts cross a pipeline boundary.**

The agents already return Pydantic models (via structured output — see `gemini-structured-output-guide.md`), so the contract is enforced at the point of generation. Don't unwrap a stage's output into a dict and rebuild it for the next stage — pass the validated model through.

```python
# Each stage's output IS its contract — validated at generation, passed through typed.
extraction: ExtractionResult = await extraction_agent.run(documents)
classification: ClassificationResult = await classification_agent.run(extraction)
compliance: ComplianceReport = await compliance_agent.run(classification)
form_m: FormMDraft = await form_m_agent.run(compliance)
```

If you ever receive an untyped dict at a boundary (e.g. data loaded from storage, or an external source), validate it into the model explicitly before using it:

```python
extraction = ExtractionResult.model_validate(raw_dict)  # raises on bad data
```

Never pass the raw dict downstream "to save a step" — that's exactly the boundary the validation contract protects.

---

## Frontend Types

The frontend uses TypeScript types for the same shapes, generated from the backend's Pydantic models (the OpenAPI schema FastAPI emits is the source). This gives the editor autocomplete and compile-time shape checking on `apps/web` without making the client a validation authority.

- The backend is the single source of truth for both validation *and* types.
- Frontend types are for developer ergonomics, not security. Any value the client sends is re-validated by Pydantic at the API boundary.
- When a Pydantic model changes, regenerate the frontend types — don't hand-edit them to drift from the backend.

---

## Best Practices

### DO

1. **Validate at the API boundary** — declare a Pydantic model for every request body.
2. **Validate at every pipeline boundary** — pass typed models, never raw dicts.
3. **Define enums once** and reuse them across models, DB, and generated frontend types.
4. **Prefer `Field` constraints** over hand-written validators for ranges and lengths.
5. **Write descriptive messages** so 422 responses are actionable.
6. **Split create / update / response models** — don't accept server-owned fields from the client.
7. **Use `model_validate`** to bring untyped external data into a model explicitly.

### DON'T

1. **Don't trust the frontend** — re-validate everything on the backend.
2. **Don't pass raw dicts across a pipeline boundary** — use the typed model.
3. **Don't duplicate enum definitions** — reuse the canonical one.
4. **Don't accept `id`/`user_id`/timestamps from the client** — the server owns them.
5. **Don't skip validation** — always validate at API and pipeline boundaries.
6. **Don't hand-edit generated frontend types** — regenerate from the backend.

---

## Common Patterns

### Pattern 1: Persisted Model + Request Models

```python
class ShipmentFields(BaseModel):
    reference: str = Field(min_length=1)
    importer_name: str = Field(min_length=1)
    notes: str | None = None


class CreateShipment(ShipmentFields):
    ...  # user_id / id / timestamps added by the service


class UpdateShipment(BaseModel):
    reference: str | None = None
    importer_name: str | None = None
    notes: str | None = None


class ShipmentResponse(ShipmentFields):
    id: str
    user_id: str
    created_at: datetime
```

### Pattern 2: Typed Pipeline Contract

```python
class ExtractionResult(BaseModel):
    supplier_name: str
    currency: str
    line_items: list[LineItem]


class ClassificationResult(BaseModel):
    items: list[Classification]   # one per extracted line item


# Stage outputs are validated models; the boundary is the contract.
extraction = await extraction_agent.run(documents)
classification = await classification_agent.run(extraction)
```

### Pattern 3: Field + Cross-Field Validation

```python
class ComplianceFlag(BaseModel):
    code: str = Field(min_length=1)
    severity: str
    blocking: bool

    @field_validator("severity")
    @classmethod
    def known_severity(cls, v: str) -> str:
        if v not in {"info", "warning", "critical"}:
            raise ValueError("severity must be one of: info, warning, critical")
        return v

    @model_validator(mode="after")
    def critical_blocks(self) -> "ComplianceFlag":
        if self.severity == "critical" and not self.blocking:
            raise ValueError("Critical flags must be blocking")
        return self
```

---

## See Also

- [Structured Output Guide](../gemini-structured-output-guide.md) — how agents produce validated Pydantic output
- [Logging Patterns](./logging.md) — logging validation failures at the boundary
