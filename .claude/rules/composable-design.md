# Composable Design — Writing Code That Composes, Tests, and Extends

---
paths:
  - "apps/api/**/services/**/*.py"
  - "apps/api/**/agents/**/*.py"
  - "apps/api/**/pipeline/**/*.py"
  - "apps/api/**/*orchestrator*.py"
  - "apps/api/**/*pipeline*.py"
---

This rule enforces composable design. `code-quality.md` covers general quality (fakes over mocks, pure functions, concern isolation). This rule covers **structural decisions** — how to decompose a feature into parts that snap together like building blocks.

The goal: every unit does one thing, accepts explicit inputs, returns explicit outputs, and can be tested/replaced/reused independently. This matters most in the agent pipeline, where extraction → classification → compliance → Form M each need to be testable in isolation.

---

## Decision: Which Pattern to Use

**Before writing any class or function**, determine the right structural pattern:

| Signal | Pattern | Example |
|--------|---------|---------|
| Coordinates 3+ external concerns (persistence, LLM agents, retrieval, notifications) | **Port-based orchestrator** | The compliance pipeline tying together repository + agents + RAG retriever |
| Standard CRUD + business rules on a single domain entity | **Service + repository** | `DocumentService`, `FormMService` |
| Stateless transformation, calculation, or decision logic | **Pure function** | `normalize_invoice_fields()`, `which_regulators(hs_code)`, `compute_levy()` |
| Adapts an external system to a port interface | **Thin adapter** | An S3 adapter, a Claude-backed agent implementing an `Extractor` port |

If you're unsure, default to a pure function. Promote to a class only when you need constructor-injected state.

---

## Port-Based Orchestrator Pattern

Use when coordinating multiple external systems. The orchestrator depends only on **port interfaces** (Python `Protocol`s), never on concrete infrastructure.

### Structure

```
pipeline/
├── domain/
│   ├── types.py           # Data types (Pydantic models, discriminated unions)
│   └── ports.py           # Port protocols + Noop implementations
├── application/
│   ├── orchestrator.py    # Business logic, depends ONLY on ports
│   └── pure_helpers.py    # Pure functions extracted from the orchestrator
├── infrastructure/
│   └── adapters.py        # Thin adapters wiring real implementations to ports
└── tests/
    ├── fakes.py           # Stateful fakes for every port
    ├── test_orchestrator.py
    └── test_pure_helpers.py
```

### Port Design Rules

1. **One `*Deps` object** bundles all ports for the orchestrator constructor
2. **Every port has a Noop implementation** for optional features (zero overhead when unused)
3. **Ports are `Protocol`s, never concrete classes** — the orchestrator never imports infrastructure
4. **Port methods accept plain objects** (Pydantic models / dataclasses), not SQLAlchemy rows or framework types
5. **Optional ports default to Noop** in the constructor — not conditional checks scattered through methods

```python
# domain/ports.py — define the boundary
from typing import Protocol

class Persistence(Protocol):
    async def get_document(self, document_id: UUID) -> Document | None: ...
    async def save_report(self, report: ComplianceReport) -> None: ...

class ProgressEmitter(Protocol):
    async def started(self, document_id: UUID) -> None: ...
    async def completed(self, document_id: UUID) -> None: ...

class NoopProgressEmitter:
    async def started(self, document_id: UUID) -> None: ...
    async def completed(self, document_id: UUID) -> None: ...

# application/orchestrator.py — depend only on ports
@dataclass
class PipelineDeps:
    persistence: Persistence
    retriever: RegulatoryRetriever
    progress: ProgressEmitter = field(default_factory=NoopProgressEmitter)

class CompliancePipeline:
    def __init__(self, config: PipelineConfig, deps: PipelineDeps):
        self._config = config
        self._deps = deps
```

### Fake Design Rules

Follow the fake pattern from `code-quality.md`, scoped to ports:

1. **Fakes implement the port protocol** and store real state (dicts, lists)
2. **Fakes expose test-only helpers** not on the protocol (`.saved_reports`, `.seed()`)
3. **Fakes support failure simulation** via `fail_on_x = True` flags
4. **A `make_fake_deps()` factory** returns all fakes:

```python
def make_fake_deps() -> PipelineDeps:
    return PipelineDeps(
        persistence=FakePersistence(),
        retriever=FakeRetriever(),
        progress=FakeProgressEmitter(),
    )
```

### Adapter Rules

The adapter is **deliberately thin** — it wires port implementations and calls the orchestrator. If the adapter contains business logic, it belongs in the orchestrator. A Claude-backed `Extractor` adapter, for example, formats the prompt and parses the typed result — it does not decide compliance.

```python
# infrastructure/adapters.py — THIN, no business logic
def build_pipeline(session: AsyncSession) -> CompliancePipeline:
    deps = PipelineDeps(
        persistence=PostgresPersistence(session),
        retriever=PgVectorRetriever(session),
        progress=DbProgressEmitter(session),
    )
    return CompliancePipeline(default_config(), deps)
```

---

## Pure Function Extraction

Any logic that doesn't need I/O must be extracted as a pure function. This is the single highest-leverage composability technique.

### When to Extract

- Ordering / sequencing logic (pipeline stage order, dependency resolution)
- Validation beyond Pydantic schema parsing
- Data transformation, mapping, filtering (normalizing extracted invoice fields)
- Decision logic (which regulators apply to an HS code, confidence scoring, routing)
- Formatting / serialization (assembling the Form M prep-sheet shape)

### Shape

```python
# Pure: explicit inputs, explicit output, no side effects
def which_regulators(hs_code: str) -> list[Regulator]:
    ...

# Pure: discriminated-union return for the caller to handle
def resolve_classification(agent_output: ClassificationResult) -> Decision:
    ...
```

### Testing

Pure functions need the simplest tests in the codebase — direct assertions, no setup:

```python
def test_chemicals_route_to_nafdac_and_son():
    regulators = which_regulators("2811.22.00")
    assert Regulator.NAFDAC in regulators
    assert Regulator.SON in regulators
```

---

## Discriminated Unions for Expected Failures

Return a discriminated union from functions that can fail in expected ways, so callers handle both paths explicitly. Use alongside the typed exceptions established elsewhere.

```python
class StageOk(BaseModel):
    ok: Literal[True] = True
    result: StageResult

class StageFailed(BaseModel):
    ok: Literal[False] = False
    error: PipelineError

StageOutcome = StageOk | StageFailed

async def run_stage(...) -> StageOutcome:
    try:
        return StageOk(result=await stage.execute(...))
    except StageError as exc:
        return StageFailed(error=PipelineError.from_exc(exc))

# Caller handles both branches
outcome = await run_stage(...)
if outcome.ok:
    outputs[stage_id] = outcome.result
else:
    errors.append(outcome.error)
```

---

## Fire-and-Forget Wrapper for Non-Critical Operations

Side effects (progress events, analytics, notifications) should never kill the main flow. This extends concern isolation from `code-quality.md` into a reusable helper:

```python
async def emit_safe(coro_factory: Callable[[], Awaitable[None]]) -> None:
    try:
        await coro_factory()
    except Exception:
        logger.exception("non-critical side effect failed")

# Usage — progress emission never kills the pipeline
await emit_safe(lambda: self._deps.progress.completed(document_id))
```

---

## Composability Checklist

Before finishing any new module, orchestrator, or shared utility:

- [ ] Every external dependency accessed through a port `Protocol` or the repository layer
- [ ] Complex logic without I/O extracted as pure functions
- [ ] Discriminated unions used for expected failure paths
- [ ] Non-critical side effects wrapped in `emit_safe` or an independent try/except
- [ ] A `make_fake_deps()` factory exists for port-based code
- [ ] Noop implementations exist for optional ports
- [ ] Adapter is thin — contains zero business logic
- [ ] Configuration is pure data (a Pydantic model / dataclass, no functions or live references)
- [ ] Each function/method does one thing at one level of abstraction
