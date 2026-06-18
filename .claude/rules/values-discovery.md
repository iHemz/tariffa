---
paths:
  - "apps/api/**/*.py"
  - "apps/web/**/*.ts"
  - "apps/web/**/*.tsx"
---

# Values: Discovery & Reuse

## ⚠️ MANDATORY: Read Reference Code FIRST

**STOP before writing ANY code. Read existing implementations FIRST.**

This is **NOT optional**. Every line of code should match the patterns already in tariffa. Code that looks different from what's already there introduces inconsistency and technical debt — and as a solo founder I'm the one who pays that debt back later.

## Core Principle: Reuse Before Create

**Always prioritize discovering and reusing existing patterns, components, and solutions before creating new ones.**

**The discovery process is MANDATORY:**
1. **READ THE RELEVANT SPEC FIRST** — the docs in `/docs/` (`01-product-vision` … `07-repository-setup`). Understand the requirement, including whether a route needs auth.
2. Identify what you're building (FastAPI route, service, repository, Pydantic AI agent, TanStack Query hook, React component).
3. Find 2-3 existing implementations of the same type.
4. READ them in full.
5. Copy the structure and patterns exactly.
6. Only adapt the business logic specific to your feature.

**CRITICAL:** Skip step 1 and you'll violate a requirement. Skip steps 3-5 and you'll violate an architectural pattern. Both matter equally.

### Decision Hierarchy

1. **Discover**: Search for existing implementations
   - Backend: look at an existing domain under `apps/api` (router + service + repository + schemas) and an existing pipeline agent
   - Frontend: look at an existing feature's TanStack Query hooks and components under `apps/web`
   - Review conventions in `/docs/` and the `.claude/rules/` files

2. **Reuse**: Leverage what already exists
   - Use existing components/services as-is when they fit
   - Follow the established layering (route → service → repository; agents return typed Pydantic models)
   - Copy and adapt from a reference implementation

3. **Improve**: Enhance existing code only when necessary
   - Refactor only if there's a clear gap
   - Extend an existing pattern rather than creating a parallel one
   - Leave a short note on why, for the next session

4. **Create**: Build new only when there's a genuine gap
   - Verify nothing existing can be adapted
   - Ensure new code follows the established patterns
   - Design it to be reusable by future work

### Why This Matters

- **Consistency**: reusing patterns keeps the architecture coherent
- **Velocity**: leveraging existing work is faster than greenfield
- **Maintenance**: fewer unique implementations means an easier codebase to navigate cold
- **Quality**: battle-tested code beats new code

### Key Architectural Patterns to Reuse

**Backend (`apps/api`):**
- Routes are thin: validate via Pydantic, call a service through `Depends`, return a `response_model`. No logic, no ORM, no Claude calls in the route.
- Services own business logic and depend on a repository (persistence) and agents (LLM work).
- Repositories own all SQLAlchemy/asyncpg access — the ORM never leaks above them.
- Every agent-to-agent handoff is a validated Pydantic model. No raw dicts across a pipeline boundary.
- The compliance agent is grounded in retrieved regulatory text (RAG) — never the model's unverified knowledge.

**Frontend (`apps/web`):**
- Thin client. No business logic, no direct DB/S3/Claude calls.
- Data access is TanStack Query hooks over a single typed fetch client. Components never call `fetch` directly.
- Large uploads use the presigned-URL flow (browser → S3).

```python
# WRONG — building the service and DB session inside a route
async def create_document(payload: DocumentCreate):
    session = async_session()
    service = DocumentService(DocumentRepository(session))
    return await service.create(payload)

# RIGHT — inject the service; reuse the established dependency
async def create_document(
    payload: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.create(payload)
```

```typescript
// WRONG — raw fetch with business logic in a component
const res = await fetch("/documents");
const docs = (await res.json()).filter(/* logic that belongs in the backend */);

// RIGHT — reuse the data-layer hook
const { data: documents } = useDocuments();
```

### Examples

**Good**: "I need a request schema → reuse the Pydantic model pattern from an existing domain's `schemas.py`"
**Bad**: "I need a request schema → invent a bespoke validation approach"

**Good**: "This component is 80% of what I need → extend it with new props"
**Bad**: "This component is 80% of what I need → build a new one from scratch"

**Good**: "New endpoint → read the spec → check auth requirement → reuse router/service/repository layering → inject via `Depends`"
**Bad**: "New endpoint → assume auth → instantiate the service and open a session inside the route"

### Questions to Ask Before Creating

1. Does this already exist in the codebase?
2. Can I adapt an existing pattern to fit?
3. Have I READ a reference implementation first?
4. Does my code look structurally identical to the reference?
5. If I build this, will it be reusable for future features?
6. Am I introducing a new pattern when an established one exists?

---

**Remember**: the best code is the code you don't have to write. The second-best is code that looks identical to existing patterns. Discover, reuse, then improve or create only when justified.
