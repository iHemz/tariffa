# Code Quality: How to Write Testable, Well-Structured Code

These principles apply to ALL code in tariffa. They produce clean, testable, maintainable code that can be unit tested without infrastructure. Examples are Python (`apps/api`) because that's where the logic lives; the same principles apply to the TypeScript thin client.

---

## 1. Separate Business Logic from Infrastructure

Keep three layers distinct:

- **Routes** (`APIRouter`) — validate input, call a service, return a typed response. No logic.
- **Services** — business logic. Depend on a repository (for persistence) and on agents (for LLM work). Never touch the ORM or the Claude API directly.
- **Repositories** — own all SQLAlchemy/asyncpg access. The ORM is hidden here; nothing above this layer sees a SQLAlchemy model.

```python
# Service depends on a repository — the ORM never leaks above this line
class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self._repository = repository

    async def get(self, document_id: UUID) -> DocumentResponse:
        doc = await self._repository.get(document_id)
        if doc is None:
            raise DocumentNotFoundError(document_id)
        return DocumentResponse.model_validate(doc)
```

```python
# WRONG — running SQL / the ORM directly in a service
result = await session.execute(select(DocumentRow).where(DocumentRow.id == document_id))

# WRONG — calling the Claude API directly in a service
client.messages.create(model="claude-...", ...)

# RIGHT — persistence via repository
doc = await self._repository.get(document_id)

# RIGHT — LLM work via a Pydantic AI agent the service depends on
extraction = await self._extraction_agent.run(document_text)
```

### Coordination Code (pipeline stages, orchestrators)

When building coordination logic that touches multiple concerns, use **constructor injection** so the unit is fully testable without infrastructure:

```python
class CompliancePipeline:
    def __init__(
        self,
        repository: DocumentRepository,
        classifier: ClassificationAgent,
        compliance: ComplianceAgent,
        retriever: RegulatoryRetriever,
    ):
        self._repository = repository
        self._classifier = classifier
        self._compliance = compliance
        self._retriever = retriever

    async def run(self, document_id: UUID) -> ComplianceReport:
        doc = await self._repository.get(document_id)
        classification = await self._classifier.run(doc.extracted)
        rules = await self._retriever.for_hs_code(classification.hs_code)
        return await self._compliance.run(classification, rules)
```

The orchestrator never creates its own dependencies — they're injected, so a test can pass fakes.

---

## 2. Pure Functions for Testable Logic

Any logic that doesn't need I/O should be a pure function — no side effects, no I/O. Pure functions are tested with direct input/output assertions: no setup, no teardown, no mocking.

```python
# WRONG — logic buried inside a method that also does I/O
class FeeService:
    async def compute(self, document_id: UUID) -> Decimal:
        doc = await self._repository.get(document_id)          # I/O
        rate = Decimal("0.05") if doc.value > 1_000 else Decimal("0.02")  # logic
        await self._repository.save_fee(document_id, doc.value * rate)    # I/O
        return doc.value * rate

# RIGHT — extract the decision as a pure function
def compute_levy(declared_value: Decimal) -> Decimal:
    rate = Decimal("0.05") if declared_value > 1_000 else Decimal("0.02")
    return declared_value * rate

# The service does only I/O + calls the pure function
class FeeService:
    async def compute(self, document_id: UUID) -> Decimal:
        doc = await self._repository.get(document_id)
        levy = compute_levy(doc.value)
        await self._repository.save_fee(document_id, levy)
        return levy
```

**Rule of thumb:** If you can test it without `async`/I/O, it should be a pure function. Mapping extracted fields into a normalized shape, scoring a classification, deciding which regulator applies — all pure.

---

## 3. Fakes Over Mocks

Use real stateful implementations (fakes) for test dependencies, not `unittest.mock`/`MagicMock` assertions like `assert_called_with`. Fakes survive refactors, catch real bugs, and are reusable across test files.

```python
# WRONG — brittle mock that breaks when implementation changes
repo = MagicMock()
repo.get.return_value = Document(id=doc_id, value=Decimal("500"))
# ...
repo.get.assert_called_once_with(doc_id)  # breaks if call shape changes

# RIGHT — stateful fake that behaves like the real thing
class FakeDocumentRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Document] = {}
        self.fail_on_save = False

    async def get(self, document_id: UUID) -> Document | None:
        return self._store.get(document_id)

    async def save(self, document: Document) -> Document:
        if self.fail_on_save:
            raise RuntimeError("simulated failure")
        self._store[document.id] = document
        return document

    # Test-only helper, not on the real repository
    def seed(self, document: Document) -> None:
        self._store[document.id] = document
```

**Why fakes are better:** they store real state (assert on what was stored, not what was called), support failure simulation (`fail_on_save = True`), are reusable, and don't break when signatures shift slightly.

**When `MagicMock` is acceptable:** at deep external boundaries (the Claude API client, S3) where building a fake is impractical. Keep those mocks at the boundary, not inside individual test bodies.

---

## 4. Test Names Are Architectural Invariants

Name tests after the rule they enforce, not the behavior they observe:

```python
# WRONG — describes what happens
def test_returns_an_error(): ...
def test_calls_the_repository(): ...

# RIGHT — states the invariant being enforced
def test_rejects_an_invoice_with_no_hs_code(): ...
def test_compliance_flag_always_cites_retrieved_rule(): ...
def test_continues_when_notification_emit_fails(): ...
def test_never_claims_to_submit_to_nicis(): ...
```

When a test fails, the name should tell you *what rule was broken*, not just that something didn't work.

---

## 5. Concern Isolation

Independent concerns must be independently fallible. If a failure in A should not affect B, put them in separate `try/except` blocks:

```python
# WRONG — a failed notification prevents returning the saved result
async def complete(self, document_id: UUID) -> DocumentResponse:
    try:
        doc = await self._repository.mark_reviewed(document_id)
        await self._notifier.send(document_id)   # if this fails...
        return DocumentResponse.model_validate(doc)  # ...this never runs
    except Exception:
        ...

# RIGHT — each concern independent
async def complete(self, document_id: UUID) -> DocumentResponse:
    doc = await self._repository.mark_reviewed(document_id)

    try:
        await self._notifier.send(document_id)
    except Exception:
        logger.exception("notification failed for document %s", document_id)

    return DocumentResponse.model_validate(doc)
```

**If you find yourself asking "should this failing break that?", the answer is almost always no.** Wrap them independently. A failed notification or analytics emit must never block a successful DB write from returning.

### Pattern: pair every "started" with a terminal "finished"/"failed"

When a background pipeline run emits a "started" status, every path out — success AND failure — must emit a paired terminal status, or the user sees a stuck "running" row forever. Own the pairing in one helper rather than hand-pairing it at every call site:

```python
async def with_progress[T](
    tracker: ProgressTracker,
    work: Callable[[], Awaitable[T]],
) -> T:
    tracker.start()
    try:
        result = await work()
        tracker.complete()
        return result
    except Exception as exc:
        tracker.fail(str(exc))
        raise   # caller still sees the real error
```

One place to change emit behavior; manual sites drift, the helper cannot.

---

## 6. Composition Over Inheritance

Prefer composition. Inject collaborators; don't build deep class hierarchies.

```python
# WRONG — deep inheritance
class SpecialCompliancePipeline(AdvancedPipeline, BasePipeline): ...

# RIGHT — compose via injected collaborators
class CompliancePipeline:
    def __init__(
        self,
        classifier: ClassificationAgent,
        compliance: ComplianceAgent,
        retriever: RegulatoryRetriever,
    ): ...
```

Break a growing service into smaller collaborators with constructor injection. Each is independently testable.

---

## 7. Pure Data Over Objects With Behavior

Configuration should be plain data — no functions, no live references, no registry lookups:

```python
# WRONG — config with embedded behavior
config = {
    "stage": "compliance",
    "on_complete": lambda result: ...,
    "get_retriever": lambda: RetrieverRegistry.get(),
}

# RIGHT — pure data (a Pydantic model or a dataclass)
class StageConfig(BaseModel):
    stage: str = "compliance"
    failure_policy: Literal["best_effort", "halt"] = "best_effort"
    timeout_s: int = 180
```

---

## 8. Visible Dependencies

Dependencies should be visible at construction, not created inline inside methods:

```python
# WRONG — hidden dependency created inside a method
class DocumentService:
    async def complete(self, document_id: UUID) -> None:
        notifier = EmailNotifier()   # hidden, untraceable, untestable
        await notifier.send(...)

# RIGHT — injected via constructor, visible and swappable in tests
class DocumentService:
    def __init__(self, repository: DocumentRepository, notifier: Notifier):
        self._repository = repository
        self._notifier = notifier
```

Wire concrete implementations once, through FastAPI `Depends`. Services receive their collaborators; they don't reach out and build them.

---

## 9. Background Tasks and Agents Are Thin

A FastAPI background task should orchestrate — fetch input, call the service/pipeline, persist the result — not contain business logic. A Pydantic AI agent owns the LLM interaction and returns a typed model; the service decides what to do with it.

```python
# WRONG — business logic inside the background task
async def run_pipeline_task(document_id: UUID) -> None:
    doc = await session.get(DocumentRow, document_id)        # DB in the task
    if doc.status == "done":                                  # logic in the task
        return
    classification = decide_hs_code(doc.text)                 # logic in the task
    ...

# RIGHT — the task delegates to the pipeline service, one unit of work
async def run_pipeline_task(document_id: UUID, pipeline: CompliancePipeline) -> None:
    report = await pipeline.run(document_id)
    await pipeline.persist(report)
```

**Rule of thumb:** if a background-task body grows past a few lines of orchestration, the logic belongs in a service or a pure function.

---

## Summary: The Quality Checklist

Before finishing any feature, verify:

- [ ] SQLAlchemy/asyncpg never called outside the repository layer
- [ ] The Claude API is only reached through Pydantic AI agents, never called inline in a service or route
- [ ] Every agent-to-agent handoff is a validated Pydantic model — no raw dicts across a boundary
- [ ] Complex logic without I/O is extracted as pure functions
- [ ] Coordination code takes dependencies via constructor injection, testable with fakes
- [ ] Tests use stateful fakes for close dependencies; `MagicMock` only at external boundaries
- [ ] Test names state the invariant being enforced
- [ ] Independent concerns have independent error handling (especially notifications/side effects)
- [ ] Configuration is pure data (no functions or live references)
- [ ] Dependencies are visible — injected via constructor / `Depends`, not built inline
- [ ] Background tasks are thin — they delegate to services; logic doesn't live in the task body
- [ ] Error handling uses typed exceptions and typed catches
