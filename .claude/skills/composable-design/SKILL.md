---
name: composable-design
description: Design composable, testable code structures before implementation. Trigger for new modules, orchestrators, pipelines, coordinators, processors, complex features, or when the user says "composable", "testable design", "design this", "scaffold", or "how should I structure this".
---

# Composable Design — Structure Before Implementation

Analyze what you're building and produce a composable architecture scaffold — ports, pure functions, fakes, and adapters — before any implementation begins. The output is a structural blueprint that makes the code unit-testable, independently deployable, and easy to extend. In tariffa this matters most for the agent pipeline (`apps/api`), where each stage hands off a typed Pydantic model to the next.

## When to Use

- Starting a new module, orchestrator, pipeline stage, or shared utility
- Refactoring a monolithic service into composable parts
- Adding coordination logic that touches multiple external systems (Postgres, S3, Claude API)
- Any time you want to understand "how should I structure this"

## Core Workflow

### Phase 1: Understand the Feature

Read the spec, the relevant `/docs/` file, or the task description. Identify:

1. **What are the external systems?** (Postgres + pgvector, S3, Claude API / Pydantic AI, third-party APIs)
2. **What is the core logic?** (the business rules that don't need I/O — e.g., HS code candidate ranking, compliance rule evaluation)
3. **What are the failure modes?** (which operations are critical vs fire-and-forget)
4. **What needs to be independently testable?** (anything with branching logic)

### Phase 2: Classify the Pattern

Based on the analysis, recommend the right structural pattern:

| Signal | Pattern | tariffa Example |
|--------|---------|-----------------|
| 3+ external concerns to coordinate | Port-based orchestrator | A pipeline coordinator that calls extraction, classification, and compliance stages |
| Standard CRUD + business rules | Service + repository | A `ShipmentService` over a Postgres repository |
| Stateless transformation or decision | Pure function | `rank_hs_candidates()`, `evaluate_compliance_rule()`, `invoice_to_line_items()` |
| Wiring an external system to a port | Thin adapter | A FastAPI dependency wiring real ports (asyncpg repo, S3 client) to an orchestrator |

Most features are a **mix** — an orchestrator that calls pure functions internally and is wired by a thin adapter (a FastAPI dependency) externally.

### Phase 3: Design the Decomposition

For each feature, produce this structural breakdown:

#### 1. Port Interfaces

Identify every external dependency and define a Python `Protocol` for it. Each port should:
- Accept plain objects (Pydantic models or primitives — no SQLAlchemy rows, no framework types)
- Return plain objects or primitives
- Have a corresponding Noop implementation for optional features
- Be named for the capability (`Persistence`, `EventSink`, `DocumentStore`, `LLMClient`)

Keep the `Protocol` in a domain/ports module — the domain defines the contract; infrastructure implements it.

#### 2. Pure Functions

Extract every piece of logic that doesn't need I/O:
- Decision logic → pure function returning a discriminated result (a small tagged Pydantic model or a `Literal`-tagged union)
- Data transformation → pure function
- Validation beyond Pydantic's field validation → pure function returning a typed verdict
- Ordering/sorting/filtering → pure function

#### 3. Orchestrator or Service

The coordination layer that wires ports and pure functions together:
- **Port-based orchestrator**: constructor takes `(config, deps)`. Config is pure data (a Pydantic model). Deps is a dataclass / Pydantic model of all ports.
- **Service**: takes a repository (and any collaborators) via the constructor. Compose smaller handlers as private members when a service grows beyond ~3 concerns.

#### 4. Fakes and Test Strategy

For port-based code, design the fakes:
- Each fake implements its port `Protocol` with in-memory state (dict, list)
- Each fake exposes test-only helpers (`.get_by_id()`, `.was_stored`, `.recorded_events`)
- Each fake supports failure simulation (`fail_on_store = True`)
- A `make_fake_deps()` factory returns all fakes

For pure functions, no fakes needed — direct input/output assertions.

#### 5. Adapter

The thin production wiring:
- Creates real port implementations from infrastructure (asyncpg pool, S3 client, Claude API client)
- Passes them to the orchestrator constructor (typically via a FastAPI dependency)
- Contains zero business logic

### Phase 4: Output the Blueprint

Present the decomposition as a clear file tree with key interfaces/signatures. Format:

```
feature_name/
├── domain/
│   ├── models.py          # FeatureConfig, FeatureResult, tagged result unions (Pydantic)
│   └── ports.py           # PortA, PortB protocols + NoopPortA, NoopPortB
├── application/
│   ├── orchestrator.py    # FeatureOrchestrator(config, deps)
│   ├── helper_a.py        # Pure: helper_a(input) -> output
│   └── helper_b.py        # Pure: helper_b(input) -> output
├── infrastructure/
│   └── adapter.py         # Thin: wires real ports -> orchestrator (FastAPI dependency)
└── tests/
    ├── fakes.py           # FakePortA, FakePortB, make_fake_deps()
    ├── test_orchestrator.py
    ├── test_helper_a.py
    └── test_helper_b.py
```

This follows a `domain/` → `application/` → `infrastructure/` layering inside `apps/api`.

For each key file, show the interface signature (not the full implementation):

```python
# domain/ports.py
from typing import Protocol

class PortA(Protocol):
    async def store(self, params: StoreParams) -> str: ...

class NoopPortA:
    async def store(self, params: StoreParams) -> str:
        return "noop"

# application/orchestrator.py
from dataclasses import dataclass

@dataclass
class FeatureDeps:
    port_a: PortA
    port_b: PortB

class FeatureOrchestrator:
    def __init__(self, config: FeatureConfig, deps: FeatureDeps) -> None: ...
    async def run(self, context: RunContext) -> FeatureResult: ...

# application/helper_a.py
def compute_order(items: list[Item]) -> list[OrderedItem]: ...
```

### Phase 5: Validate Against Checklist

Before presenting, verify:

- [ ] Every external dependency behind a `Protocol` port
- [ ] Complex stateless logic extracted as pure functions
- [ ] Tagged result models for expected failure paths
- [ ] Non-critical side effects identified (will run as a background task or in an independent try/except)
- [ ] Fakes designed with real state, not `unittest.mock`
- [ ] Noop implementations for optional ports
- [ ] Adapter is thin — zero business logic
- [ ] Configuration is pure data (a Pydantic model)
- [ ] Each function/method does one thing at one level of abstraction
- [ ] File tree follows the `apps/api` module conventions

## Key Principles

### Composition over configuration
Build features from small, focused pieces that snap together. A service composing several handlers, each independently testable via constructor injection, is the canonical example.

### Ports are the boundary
The port `Protocol` is the most important design artifact. The domain layer defines the contract; infrastructure implements it. Get the port right and the orchestrator, fakes, and adapter all follow naturally.

### Pure functions are free testability
Every pure function extracted is a unit test that needs zero setup, zero teardown, and zero mocking. A set of pure guard/rule functions, all tested with direct input/output assertions, is the goal.

### Noop by default, real by injection
Optional features (analytics, lifecycle events, audit logging) use Noop implementations by default. Real implementations are injected only when explicitly enabled. Features work correctly with zero configuration and the happy path has zero overhead from unused features.

### Tagged results force correctness
Return a tagged union for functions that can fail in expected ways — e.g. `Allowed | Blocked(reason)` modeled as small Pydantic classes with a `kind: Literal[...]` discriminator. Callers must then handle both paths.

## Common Pitfalls

- **Putting logic in the adapter**: if the adapter has an `if` statement, the logic belongs in the orchestrator.
- **Ports that accept framework types**: ports should accept Pydantic models or primitives. If a port method takes a SQLAlchemy row, an asyncpg `Record`, or a FastAPI `Request`, the abstraction is leaking.
- **Skipping Noop implementations**: without Noops, optional features require conditional checks scattered through the orchestrator.
- **Using mocks instead of fakes**: mocks test that code was called. Fakes test that code worked. Fakes survive refactors; mocks break on implementation changes.
- **God functions**: if a method has more than ~30 lines, extract the pure logic into a helper. The orchestrator should read like a sequence of high-level steps.

## Reference Patterns

See `references/codebase-patterns.md` for concrete Python implementations of each pattern above — read 2-3 before producing a blueprint for any new feature.
