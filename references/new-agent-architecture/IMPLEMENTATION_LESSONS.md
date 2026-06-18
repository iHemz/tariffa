# Memory & Context Architecture: Implementation Lessons

> **Status:** Post-Implementation Retrospective
> **Purpose:** Capture the gap between a planned context/memory architecture and what actually shipped, as portable lessons for future work.

---

## Overview

This document captures lessons from implementing a layered memory and context architecture for an LLM agent pipeline. It compares the original design with what was actually built — what worked, what was simplified, and what emerged only once the system met real workloads. The specifics below are deliberately stack-agnostic where the lesson is portable; where stack matters, they assume tariffa's `apps/api` stack: FastAPI, Pydantic AI, Postgres + pgvector, S3, Claude (Anthropic).

---

## Key Differences: Plan vs Implementation

### 1. Tiered selection — simplified to a toggle

**Documented plan:** a three-tier system that automatically classified each task and picked a context strategy.

```python
# Proposed: automatic tier selection
AgentTier = Literal["fast", "context-aware", "memory-enhanced"]

def select_tier(
    task_type: str,
    history_length: int,
    requires_historical_knowledge: bool,
) -> AgentTier:
    ...
```

**Actual implementation:** a simple on/off toggle.

```python
# Memory enabled per-run via a flag
result = await agent.run(prompt, use_memory=True)
```

**Lesson:** automatic tier classification was over-engineered. A boolean toggle proved sufficient. The caller knows whether a stage needs memory retrieval better than an automated classifier does — and the classifier was just one more thing to debug.

---

### 2. A separate "with memory" entry point — merged into the existing call

**Documented plan:** a distinct `run_with_memory()` method alongside the normal run path.

**Actual implementation:** memory integrated into the existing run path, gated by the toggle. When enabled, the run automatically logs the input to the session store, compiles working context from the layered model, and logs the output after completion.

**Lesson:** a separate method bloated the API surface and forced callers to choose an entry point. Integrating memory into the existing path with conditional activation was cleaner and required no changes to call sites.

---

### 3. Domain-specific memory schema — replaced with generic types

**Documented plan:** a bespoke schema for recording stage outcomes, with domain-specific fields baked into the storage layer.

**Actual implementation:** generic memory types carry everything via flexible `tags` and `metadata`.

```python
MemoryType = Literal[
    "domain_knowledge",
    "learned_heuristic",
    "entity_context",
    "constraint",
    "insight",
]
```

**Lesson:** generic memory types with flexible `tags`/`metadata` proved sufficient. Domain-specific shapes (e.g. "this regulator rejected this HS code for this reason") can be layered on in application code rather than baked into infrastructure. Don't prematurely specialise the storage layer.

---

### 4. External memory service — deferred

**Documented plan:** integrate a third-party memory service over a network call.

**Actual implementation:** local storage only — an in-process store for development and a pgvector-backed store for production.

**Lesson:** external dependencies add latency and operational surface. Postgres + pgvector provides sufficient semantic retrieval for the MVP. An external service can be added later as another memory-source adapter without architectural changes — so there was no reason to take the dependency early.

---

### 5. Factory pattern — emerged from production needs

**Not documented:** no factory was planned.

**Actual implementation:** environment-based factory selection.

```python
def get_memory_store() -> MemoryStore:
    if settings.environment == "production" or settings.use_vector_memory:
        return VectorMemoryStore(...)   # pgvector
    return InMemoryStore()              # dev / tests
```

**Lesson:** the dev-vs-production split wasn't anticipated. A factory with environment-based selection emerged naturally and should be planned for upfront in future designs — tests and local dev want a cheap in-memory store; production wants the real vector store.

---

### 6. Hybrid search — a significant, unplanned enhancement

**Documented plan:** basic vector search over embeddings.

**Actual implementation:** hybrid search combining semantic (vector) and lexical (full-text) retrieval, merged with Reciprocal Rank Fusion (RRF).

```python
# Run both searches, then merge by rank
vector_hits = await store.vector_search(query_embedding, limit=k)
text_hits = await store.text_search(query, limit=k)
merged = merge_rrf(vector_hits, text_hits, k=60, limit=limit)
```

**Lesson:** vector-only search has recall gaps — especially for exact regulatory terms, HS codes, and regulator names where lexical match matters. Hybrid retrieval with RRF significantly improved result quality. Plan for a text-search fallback from day one; don't assume embeddings alone are enough.

---

### 7. Reflection — moved to a background task

**Documented plan:** run reflection inline, right after a session completed.

**Actual implementation:** reflection runs as a FastAPI background task, decoupled from the request.

```python
@router.post("/runs/{run_id}/complete")
async def complete_run(run_id: str, background_tasks: BackgroundTasks):
    # ... finalize the run ...
    background_tasks.add_task(reflect_on_session, run_id)
    return {"status": "completed"}
```

**Lesson:** inline reflection added latency to every interaction. Running it as a background task is better for UX — the user gets their result immediately, and learnings are extracted afterward. Design for background reflection (event-driven or task-queue) from the start.

---

### 8. Session persistence — critical, and under-specified

**Not documented in detail:** snapshot/restore of session state between requests.

**Actual implementation:** explicit snapshot and restore.

```python
def snapshot(self) -> SessionSnapshot:
    return SessionSnapshot(
        session_id=self.session_id,
        events=list(self.events),
        created_at=self.created_at,
        updated_at=self.updated_at,
    )

@classmethod
def from_snapshot(cls, snapshot: SessionSnapshot) -> "SessionStore":
    store = cls(snapshot.session_id)
    store.events = list(snapshot.events)
    store._rebuild_indexes()
    return store
```

**Lesson:** because the API is stateless across requests, session state must be persisted and rehydrated explicitly. The snapshot/restore pattern is essential and should be a first-class concern, not an afterthought.

---

### 9. Vector index management — more complexity than expected

**Not documented:** index creation and migration weren't planned.

**Actual implementation:** explicit index management for the pgvector store — creating the vector index and supporting metadata filters, with a migration path for production.

**Lesson:** vector indexes require deliberate creation and can take time to build on a populated table. Auto-creating in development plus migration scripts for production is the right pattern. This operational concern should be documented upfront, not discovered during deployment.

---

### 10. Cache stability — only partially applied

**Documented plan:** comprehensive prompt-cache stability with a stable system-prompt prefix and explicit cache breakpoints across all agents.

**Actual implementation:** the cache-stability utilities exist but aren't applied uniformly. Some agents interpolate volatile content into their prefix and silently miss the cache.

**Lesson:** cache stability requires discipline across the whole codebase, not just available utilities. With Claude prompt caching the cost difference between a hit and a miss is large, but the benefit only lands if every agent keeps a stable prefix (no timestamps, deterministic serialisation, volatile content after the breakpoint). Enforce it via review or lint, not good intentions.

---

## What Worked Well

### 1. The layered model was conceptually sound
Separating Working Context → Session → Memory → Artifacts proved valuable even where not every layer was fully utilised. It gave a clear vocabulary for deciding what belonged where.

### 2. Failure tracking in the session
Recording failed attempts prevented the agent from repeating mistakes within a run — the "keep wrong stuff in" principle held up. For the classification stage, remembering "this code was already rejected" measurably reduced loops.

### 3. Schema-driven summarisation
A summary schema that preserved causal steps, active constraints, failed attempts, and open questions kept the critical structure intact through compression. Blind "summarise to save space" would have dropped exactly the regulatory edge cases that matter.

### 4. Token-budget awareness
A context compiler that estimated tokens and budgeted them prevented overflow gracefully instead of failing at the model boundary.

### 5. Tracing throughout
Tracing every memory operation made debugging and performance analysis tractable — and is what made the audit story (reconstruct what the model saw) credible.

---

## What Was Over-Engineered

1. **Automatic tier selection** — a toggle sufficed.
2. **Separate entry points per strategy** — one path with config options is cleaner.
3. **Domain-specific memory schema** — generic types with tags achieved the same flexibility without schema proliferation.

---

## What Was Under-Specified

1. **Production deployment concerns** — factory for environment selection, index management and migration, connection pooling, error handling and fallbacks.
2. **Stateless-request considerations** — session persistence between requests, store initialisation timing.
3. **Testing strategy** — how to test retrieval quality, fixtures for session trajectories, mocking embeddings.

---

## Recommendations for Future Implementations

1. **Start simple.** Begin with an in-memory store and a toggle. Add complexity only when you feel the pain.
2. **Plan for hybrid search.** Don't assume vector search alone is sufficient — plan for a lexical fallback from day one.
3. **Design for background reflection.** Reflection is background work, not inline. Plan for a task-queue or event-driven path.
4. **Document operational concerns.** Index creation, migrations, connection management, and monitoring deserve first-class documentation.
5. **Enforce cache stability.** Create lint rules or a review checklist for cache-stable prompt prefixes.
6. **Persist sessions first.** Across stateless requests, snapshot/restore is essential — design it in from the start.

---

## Metrics to Track

Track these from day one:

| Metric | Why It Matters |
|--------|----------------|
| Memory retrieval latency (p50, p99) | User-perceived slowdown |
| Prompt-cache hit rate | Large cost difference per request |
| Memory recall accuracy | Are relevant memories actually retrieved? |
| Session event-count distribution | Are sessions growing unbounded? |
| Reflection lesson acceptance rate | Are extracted lessons useful? |
| Hybrid-search contribution | How often does lexical search rescue a vector miss? |

---

## Related Documentation

- [Context Engineering for Long-Running AI Agents](./context-engineering-for-agents.md)
