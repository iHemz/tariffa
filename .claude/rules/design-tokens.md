# Design Tokens

---
paths:
  - "apps/web/**/*.tsx"
  - "apps/web/**/*.css"
---

Rules for using the tariffa design token system. Tokens are defined in Tailwind CSS v4 via the `@theme` block in the global stylesheet (`apps/web/app/globals.css`). Tailwind v4 turns each `@theme` entry into a CSS variable AND a matching utility class.

> **Guiding lens:** Imagine a Nigerian clearing agent using this for the first time, on whatever device is in front of them. They cannot tell `#2563EB` from `--color-primary` — but they will absolutely notice when a button looks "off", contrast fails, or spacing feels uneven. Tokens exist so a first-time user always gets a polished, consistent experience without you thinking about it.

## Define tokens once, in `@theme`

```css
/* apps/web/app/globals.css */
@import "tailwindcss";

@theme {
  --color-primary: #2563eb;
  --color-success: #16a34a;
  --color-warning: #d97706;
  --color-danger: #dc2626;
  --color-surface: #ffffff;
  --color-muted: #6b7280;

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;

  --radius-card: 0.625rem;   /* 10px */
}
```

Each entry is usable as both a utility (`bg-primary`, `text-danger`, `rounded-card`, `font-sans`) and a variable (`var(--color-primary)`) in raw CSS.

## Color System

Use semantic token utilities, never raw hex values:

```tsx
// WRONG — hardcoded hex
<p style={{ color: "#2563eb" }}>

// WRONG — arbitrary value that bypasses the token
<p className="text-[#2563eb]">

// RIGHT — semantic token utility
<p className="text-primary">
<span className="bg-success/10 text-success">Cleared</span>
<span className="text-danger">Compliance issue</span>
```

| Token | Purpose |
|-------|---------|
| `primary` | Brand blue — primary actions, links, focus |
| `success` | Green — passed checks, positive flags |
| `warning` | Amber — caution, "needs review" |
| `danger` | Red — compliance failures, destructive actions |
| `surface` | Card / panel backgrounds |
| `muted` | Secondary / dimmed text and borders |

For opacity, use Tailwind's slash syntax (`bg-success/10`) rather than defining new shade tokens.

## Typography

Font family is set on `<body>` via the `font-sans` token — don't set `font-family` ad hoc. Use Tailwind's type scale for size and weight:

```tsx
<h1 className="text-3xl font-semibold">Form M Prep Sheet</h1>
<p className="text-base">Body copy</p>
<span className="text-sm text-muted">Helper text</span>
```

## Spacing Scale

Use Tailwind's spacing scale (multiples of `0.25rem`) — never hardcoded pixels:

```tsx
<div className="flex flex-col gap-4">   {/* 16px vertical gap */}
<div className="flex items-center gap-2">  {/* 8px horizontal gap */}
<section className="p-6">                 {/* 24px padding */}
<div className="py-8">                    {/* 32px vertical padding */}
```

Rough mapping: `gap-1` = 4px, `gap-2` = 8px, `gap-4` = 16px, `gap-6` = 24px, `gap-8` = 32px.

## Component Conventions

Compose primitives with shared utility sets rather than overriding per-instance. A card:

```tsx
<div className="rounded-card bg-surface p-6 shadow-sm">
```

If the same className string repeats, extract a small component (e.g. `<Card>`), not a one-off override.

## State Patterns

Keep loading / empty / error states consistent across screens:

```tsx
// Loading
{isLoading && <Skeleton className="h-24 w-full" />}

// Empty
{!isLoading && items.length === 0 && (
  <EmptyState title="No documents yet" description="Upload an invoice to start" />
)}

// Error
{isError && <p className="text-danger">{error.message}</p>}

// Button loading
<Button disabled={isPending}>{isPending ? "Saving…" : "Save"}</Button>
```

## Dark Mode (when added)

If/when dark mode lands, drive it with the `dark:` variant and theme-aware tokens — not by swapping hardcoded hex. Define light/dark values for surface and text tokens via CSS variables under a `.dark` selector, then reference the same utility everywhere so it adapts automatically. Don't pin a surface background to a fixed color that only reads correctly in one scheme.

## Rules

1. **Never hardcode colors** — use token utilities (`text-primary`), not hex or `text-[#...]` arbitrary values
2. **Never hardcode spacing** — use the Tailwind spacing scale
3. **Never set a custom `font-family`** — the `font-sans` token handles it globally
4. **Add a new token before reaching for an arbitrary value** — extend `@theme`, don't sprinkle `[...]`
5. **Extract repeated className sets into components** rather than duplicating them
6. **Use consistent loading/empty/error patterns** across every screen
