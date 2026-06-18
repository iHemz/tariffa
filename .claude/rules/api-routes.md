---
paths:
  - "apps/api/**/*.py"
  - "apps/web/**/hooks/**/*.ts"
  - "apps/web/**/api/**/*.ts"
---

# API Conventions

tariffa is split across two apps. **All routes, business logic, validation, and AI orchestration live in the FastAPI backend (`apps/api`).** The Next.js frontend (`apps/web`) is a thin client — it never talks to Postgres, S3, or the Claude API directly; it only calls the FastAPI backend through a typed data layer.

There is **no Next.js API-route layer** and no `withAuth`/`withDb`/`withValidation` HOF chain. If you're reaching for those, you're in the wrong app.

---

## Part 1 — FastAPI Backend Routes (`apps/api`)

### 1. Routers, not loose handlers

Group endpoints into `APIRouter` modules by domain (documents, classification, compliance, form-m). Mount them in the app factory. Keep route functions thin: validate input, call a service, return a typed response.

```python
from fastapi import APIRouter, Depends
from app.documents.service import DocumentService
from app.documents.schemas import DocumentCreate, DocumentResponse
from app.dependencies import get_document_service, get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse)
async def create_document(
    payload: DocumentCreate,
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.create(payload, user_id=user.id)
```

### 2. Validation is Pydantic, at the boundary

Request and response bodies are Pydantic models. FastAPI validates the request automatically — never hand-parse the body. Declare `response_model` so the response is validated and serialized through a typed contract too.

- Request models live next to the router (`schemas.py` per domain).
- Every agent-to-agent handoff inside the pipeline is also a Pydantic model, validated before it crosses a stage boundary. No raw dicts crossing a boundary.

### 3. Dependency injection via `Depends`

Wire services, the DB session, and the current user through FastAPI's `Depends`. Don't instantiate services or open DB sessions inside a route body.

```python
# WRONG — building the service and session inside the route
async def create_document(payload: DocumentCreate):
    session = async_session()
    service = DocumentService(DocumentRepository(session))
    ...

# RIGHT — injected
async def create_document(
    payload: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
):
    ...
```

Routes call **service methods**, not the repository or the ORM directly. Postgres (SQLAlchemy/asyncpg) stays behind the repository layer.

### 4. Auth

Single-tenant. A simple auth dependency (`get_current_user`) resolves the user and is attached to protected routes via `Depends`. Public routes (health check, webhooks) just omit it. There is no org/tenant filtering — do not add `org_id` scoping.

### 5. Errors

Raise typed exceptions; let an exception handler map them to HTTP responses. Don't build raw `JSONResponse` error bodies in route functions.

```python
from fastapi import HTTPException

# Simple cases
raise HTTPException(status_code=404, detail="Document not found")

# Or domain exceptions mapped by a registered handler
raise DocumentNotFoundError(document_id)
```

### 6. Long-running and file work

- Pipeline runs (extraction → classification → compliance → Form M) that exceed a request budget run as **FastAPI background tasks**, not inline in the response.
- Large file uploads go **browser → S3 directly via a presigned URL** the backend issues. Don't proxy file bytes through both `web` and `api`.

### 7. Never in a backend route

- ❌ Direct SQLAlchemy/asyncpg queries (use the repository via a service)
- ❌ Direct Claude API calls (orchestrate through Pydantic AI agents/services)
- ❌ Hand-parsed request bodies (use Pydantic models)
- ❌ `org_id` / tenant filtering (single-tenant)

---

## Part 2 — Frontend Data Layer (`apps/web`)

The frontend reaches the backend through **TanStack Query hooks** wrapping a small typed fetch client. Components never call `fetch` directly and never hold business logic.

### 1. One typed fetch client

A single client module builds the request to the FastAPI base URL and parses the typed response. Hooks use it; components use hooks.

```typescript
// apps/web/lib/api-client.ts
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) throw await toApiError(res);
  return (await res.json()) as T;
}
```

### 2. Queries for reads

```typescript
// apps/web/features/documents/hooks/useDocuments.ts
"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import type { DocumentResponse } from "../types";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: () => apiFetch<DocumentResponse[]>("/documents"),
  });
}
```

### 3. Mutations for writes, with invalidation

```typescript
"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import type { DocumentResponse, DocumentCreate } from "../types";

export function useCreateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: DocumentCreate) =>
      apiFetch<DocumentResponse>("/documents", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}
```

### 4. File uploads use the presigned-URL flow

For uploads, the hook asks the backend for a presigned S3 URL, then `react-dropzone` + the browser PUTs the file straight to S3. The file bytes never pass through the Next.js layer.

### 5. Never in the frontend

- ❌ Direct calls to Postgres, S3, or the Claude API
- ❌ Business logic, classification, or compliance rules (those live in `apps/api`)
- ❌ Raw `fetch` in components — go through a TanStack Query hook
- ❌ Stringly-typed responses — type every payload to match the backend Pydantic model

---

## Before Writing Any Endpoint or Hook

1. Read the relevant spec in `/docs/` — does this route need auth, or is it public?
2. Backend: add/extend an `APIRouter`, define Pydantic request/response models, call a service via `Depends`, raise typed errors.
3. Frontend: add a TanStack Query hook over the typed fetch client; invalidate the right query keys on mutation.
4. Keep the boundary clean — logic in `apps/api`, presentation and data-fetching wiring in `apps/web`.
