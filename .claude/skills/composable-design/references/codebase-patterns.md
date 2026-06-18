# Composable Design — tariffa Reference Patterns

These are the patterns the composable-design skill builds upon, expressed for tariffa's stack (`apps/api`: FastAPI, Pydantic AI, Postgres + pgvector, S3, Claude API). Read these when you need to understand how a specific pattern is implemented, not just what it looks like in the abstract.

---

## Pattern 1: Domain-Layer Port (Protocol)

A port is a `Protocol` that lives in the **domain layer**, not infrastructure. Application code depends on the protocol, never on asyncpg/SQLAlchemy directly:

```python
from typing import Protocol

class ShipmentRepository(Protocol):
    async def find_by_id(self, shipment_id: str) -> Shipment | None: ...
    async def atomic_update(self, shipment_id: str, update: dict[str, object]) -> Shipment | None: ...
    async def find(self, filter: dict[str, object], limit: int = 50) -> tuple[list[Shipment], int]: ...
```

Key insight: the protocol describes *what the application needs*, in plain Pydantic types — the domain defines the contract shape; infrastructure provides the concrete asyncpg implementation. For optional ports, define a **Noop implementation** next to the protocol — it's a production artifact, not test code.

```
1. Define the Protocol in domain/ (what the orchestrator needs)
2. Provide a Noop (zero overhead when the feature is off)
3. Orchestrator constructor picks Noop or real based on config
4. Adapter provides the real implementation in production (FastAPI dependency)
5. Fake provides a testable implementation in tests
```

---

## Pattern 2: Constructor Injection Handler

A handler receives all dependencies via constructor — repository, mappers, and event sinks:

```python
class ShipmentAdminHandler:
    def __init__(
        self,
        repository: ShipmentRepository,
        to_response: Callable[[Shipment], ShipmentResponse],
        find_by_id: Callable[[str], Awaitable[ShipmentResponse | None]],
        emit_flagged: Callable[..., Awaitable[None]],
    ) -> None:
        self._repository = repository
        self._to_response = to_response
        self._find_by_id = find_by_id
        self._emit_flagged = emit_flagged
```

One constructor, all dependencies visible. No hidden client construction inside methods. The handler never creates its own dependencies — the parent service wires everything at construction time.

---

## Pattern 3: Service Composing Multiple Handlers

A service composes several independent handlers, delegating per operation:

```python
class ShipmentService:
    def __init__(self, repository: ShipmentRepository) -> None:
        self._repository = repository
        self._admin = ShipmentAdminHandler(repository, self._to_response, self.find_by_id, self._emit_flagged)
        self._review = ShipmentReviewHandler(repository, ...)
        self._export = FormMExportHandler(repository, ...)
```

Each handler is independently testable via constructor injection. This is the recommended approach when a service grows beyond ~3 concerns.

---

## Pattern 4: Pure Functions with Tagged Results

Pure domain logic is the gold standard — functions that take plain data and return a typed verdict, with zero I/O. Model the verdict as a tagged union of small Pydantic classes:

```python
from typing import Literal
from pydantic import BaseModel

class Allowed(BaseModel):
    kind: Literal["allowed"] = "allowed"

class Blocked(BaseModel):
    kind: Literal["blocked"] = "blocked"
    reason: str

ComplianceVerdict = Allowed | Blocked

def evaluate_regulator_rule(item: ClassifiedItem, rule: RegulatoryRule) -> ComplianceVerdict:
    if rule.requires_registration and not item.has_registration:
        return Blocked(reason=f"{rule.regulator} registration required")
    return Allowed()
```

Key patterns:
- **Input types are minimal** — pass only the fields the function needs, not the full row.
- **The tagged union forces exhaustive handling** — callers must inspect `kind` before proceeding.
- **Multiple verdict types** for different decisions (compliance, classification confidence, etc.).

Testing is trivial — direct assertions, no setup:

```python
def test_blocks_unregistered_item():
    verdict = evaluate_regulator_rule(
        ClassifiedItem(has_registration=False),
        RegulatoryRule(regulator="NAFDAC", requires_registration=True),
    )
    assert verdict == Blocked(reason="NAFDAC registration required")
```

---

## Pattern 5: Pure Data Transformation Bridge

A pure bridge converts one representation into another with no I/O and no side effects:

```python
def invoice_to_line_items(
    invoice: ExtractedInvoice,
    overrides: LineItemOverrides | None = None,
) -> list[LineItem]:
    items = [_normalize(row) for row in invoice.rows]
    if overrides:
        items = _apply_overrides(items, overrides)
    return items
```

Key patterns:
- **Helper functions are private (module-scoped)** — `_normalize`, `_apply_overrides`.
- **One public entry point** — callers use `invoice_to_line_items()`, internals are hidden.
- **Merging with priority** — explicit overrides take precedence over extracted values.

---

## Pattern 6: Stateless Delegation

A class can group related methods while staying stateless — no constructor dependencies:

```python
class HsClassifier:
    async def classify_items(
        self,
        items: list[LineItem],
        context: ClassificationContext,
        preview_only: bool = False,
    ) -> list[ClassifiedItem]:
        ...
```

A service delegates here for classification while retaining ownership of persistence, status transitions, and events. This separation means the classifier can be tested with stubbed Claude responses without touching the database.

---

## Pattern 7: Abstract Processor Base

An abstract base extracts reusable document-processing logic. Subclasses implement only the domain-specific parts:

```python
from abc import ABC, abstractmethod

class DocumentProcessorBase(ABC):
    def __init__(self, job_id: str, blob_url: str, config: ProcessingConfig) -> None: ...

    # Concrete: shared logic
    async def download(self) -> bytes: ...
    async def detect_duplicates(self, parsed: ParseResult) -> ResultWithDuplicates: ...

    # Abstract: subclass-specific
    @abstractmethod
    async def parse(self, content: bytes) -> ParseResult: ...
    @abstractmethod
    def completion_event(self) -> str: ...
```

Key patterns:
- **Config as a data object** — `ProcessingConfig` is a Pydantic model with defaults.
- **Result types** are well-defined Pydantic models.
- **No framework dependency** — the base class is usable from API routes, background tasks, and tests.

---

## Pattern 8: Clean Domain Types

Domain types are plain Pydantic models, database-agnostic:

```python
# Architectural rules for this module:
# - May import domain models and shared types
# - Must NOT import infrastructure (asyncpg/SQLAlchemy) or application layers

from enum import StrEnum

class ShipmentStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_REVIEW = "awaiting_review"
    READY_TO_FILE = "ready_to_file"

class Shipment(BaseModel):
    id: str
    status: ShipmentStatus
```

Key patterns:
- **`StrEnum` as the single source of truth** for status values.
- **Pydantic models** for complex types.
- **Explicit import-boundary comments** documenting what the module may import.

---

## Pattern 9: Service + Repository (Module Pattern)

For standard domain modules (not coordination code), the simpler pattern:

```python
class ShipmentService:
    def __init__(self, repository: ShipmentRepository) -> None:
        self._repository = repository

    def _to_response(self, entity: Shipment) -> ShipmentResponse: ...
    async def create(self, request: CreateShipment) -> ShipmentResponse: ...
    async def update(self, shipment_id: str, request: UpdateShipment) -> ShipmentResponse: ...
```

The repository hides asyncpg/SQLAlchemy. The service is wired once via a FastAPI dependency. Events are emitted as background tasks wrapped in try/except so a failed side effect never breaks the request.

This is the right pattern for ~80% of modules. Reserve port-based orchestration for the ~20% that coordinate multiple external systems.

---

## Pattern 10: `make_fake_deps()` for Tests

The recommended approach for testing port-based orchestrators:

```python
@dataclass
class FakeDeps:
    persistence: "FakePersistence"
    document_store: "FakeDocumentStore"

def make_fake_deps() -> FakeDeps:
    return FakeDeps(
        persistence=FakePersistence(),
        document_store=FakeDocumentStore(),
    )
```

The fake satisfies the orchestrator's deps **and** exposes concrete fake types, so tests can assert on `.was_stored` / `.get_by_id()` directly.

Fakes should support failure simulation:

```python
class FakePersistence:
    def __init__(self) -> None:
        self.fail_on_store = False
        self._stored: list[StoreParams] = []
        self._next_id = 1

    async def store(self, params: StoreParams) -> str:
        if self.fail_on_store:
            raise RuntimeError("configured to fail")
        self._stored.append(params)
        ident = f"fake-id-{self._next_id}"
        self._next_id += 1
        return ident
```

Tests flip `deps.persistence.fail_on_store = True` to verify graceful error handling — no need for `mock.patch(..., side_effect=...)`.
