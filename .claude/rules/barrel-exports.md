# Barrel Export Safety: Keep Client-Only Code Out of Server Components

---
paths:
  - "apps/web/**/index.ts"
  - "apps/web/**/index.tsx"
---

## The Problem

Next.js (App Router) renders Server Components by default. A barrel file (`index.ts`) that re-exports React hooks — anything using `useState`, `useEffect`, `useRef`, or TanStack Query's `useQuery`/`useMutation` — gets pulled into the server graph the moment a Server Component imports *anything* from that barrel. Because the bundler evaluates the whole import chain before tree-shaking, a single hook in the chain triggers a build error even if the server file never uses it.

## The Rule

**Never re-export React hooks (or TanStack Query hooks) through a barrel that a Server Component imports.** Keep hooks out of shared barrels; import them directly from their source file in the `"use client"` component that needs them.

### What to do instead

1. **Shared barrels export only client-safe things** — types, constants, and pure helpers. No hooks.
   ```typescript
   // apps/web/features/documents/index.ts
   export type { ExtractedDocument } from "./types";
   export { DOCUMENT_STATUSES } from "./constants";
   // No `export * from "./hooks"` — hooks are imported directly.
   ```

2. **Components import hooks directly from their source files**:
   ```typescript
   // WRONG — barrel re-export risks pulling a hook into the server graph
   import { useDocuments } from "../";
   import { useDocuments } from "../hooks";

   // RIGHT — direct import from the source file
   import { useDocuments } from "../hooks/useDocuments";
   import { useUploadDocument } from "../hooks/useUploadDocument";
   ```

3. **Every file that exports a hook must start with `"use client"`.**

### Why this matters

- The data layer in `apps/web` is TanStack Query hooks that call the FastAPI backend. These are client-only by definition.
- A shared barrel is safe for both server and client *only* if it contains no client-only code.
- Next.js tree-shaking does NOT save you — the bundler evaluates the import chain before shaking.

### How to verify

If you add a new hook or change hook exports, run:
```bash
pnpm --filter web run build
```
A build error mentioning `useState`/`useEffect`/`useRef` "only works in a Client Component" means a hook leaked through a barrel into the server graph.
