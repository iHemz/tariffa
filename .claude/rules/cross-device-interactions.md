# Cross-Device Interactions

---
paths:
  - "apps/web/**/*.tsx"
  - "apps/web/**/*.css"
---

Rules for building interactions that work across desktop, tablet, and mobile.

> **Guiding lens:** Imagine a Nigerian clearing agent doing this task for the first time — on a phone, on a tablet, with a trackpad, with a touchscreen. They will not know which interactions are "hover-only" vs "tap-only". Every interactive element must work the first time, on every device, without prior context.

## No JavaScript Hover Events

Never use `onMouseEnter` or `onMouseLeave` for visual hover effects. They don't fire on touch devices and create inconsistent experiences.

```tsx
// WRONG — JavaScript hover events drive a visual state
<div onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}>

// RIGHT — CSS-only hover via Tailwind's hover: variant
<div className="shadow-sm transition-shadow hover:shadow-md">
```

**Exception:** `onMouseEnter`/`onMouseLeave` are acceptable for non-visual logic like analytics or prefetching.

## Responsive Layout Patterns

Use Tailwind's mobile-first breakpoint prefixes — the base utility is the mobile default, prefixed utilities layer on at larger widths:

```tsx
// Full width on mobile, half on desktop
<div className="w-full lg:w-1/2">

// Responsive grid column count
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">

// Responsive image sizing
<img className="w-full md:w-[400px]" />
```

### Navigation Collapse

Collapse the nav into a toggle on small screens, expand inline on larger ones — drive it with breakpoint utilities and a `useState` toggle, not hover:

```tsx
<nav className="hidden md:flex">{/* desktop nav */}</nav>
<button className="md:hidden" onClick={() => setOpen((o) => !o)}>Menu</button>
{open && <nav className="md:hidden">{/* mobile drawer */}</nav>}
```

### Breakpoints (Tailwind defaults)

| Prefix | Min width | Use for |
|--------|-----------|---------|
| (none) | 0px+ | Mobile default |
| `sm` | 640px+ | Large phones |
| `md` | 768px+ | Tablets |
| `lg` | 1024px+ | Desktop |
| `xl` | 1280px+ | Large desktop |

Always design **mobile-first** — the unprefixed utility is the default, prefixed utilities add complexity for larger screens.

## Touch Targets

- Minimum touch target: 44×44px (WCAG 2.5.5) — e.g. `min-h-11 min-w-11` on icon buttons
- Give interactive elements real padding (`px-4 py-2`), not just a tight label
- Add adequate spacing between clickable elements on mobile (`gap-3`+)

## Click Over Hover

All interactive states must be click/tap activated, not hover-dependent. Content that only appears on hover is invisible on touch:

```tsx
// WRONG — detail only reachable via hover tooltip
<span title="Details" className="group">
  <Info /> <span className="hidden group-hover:block">…</span>
</span>

// RIGHT — detail reachable via click (popover/disclosure)
<button onClick={() => setOpen((o) => !o)} className="min-h-11 min-w-11">
  <Info />
</button>
{open && <div className="…">Details here</div>}
```

## CSS Hover Safety

Wrap meaningful hover-only styling in the `hover:hover` media query to avoid sticky hover on touch devices. Tailwind v4 exposes this via the `hover-hover:` variant (or a raw media query in CSS):

```css
@media (hover: hover) {
  .card:hover { box-shadow: var(--shadow-md); }
}
```

Tailwind's `hover:` variant already only applies on real pointers in modern configs, but for custom CSS, be explicit.

## Cursor Management

Set appropriate cursors on interactive elements:

```tsx
<div className="cursor-pointer" onClick={handleClick}>
<button className="cursor-pointer disabled:cursor-not-allowed">
```
