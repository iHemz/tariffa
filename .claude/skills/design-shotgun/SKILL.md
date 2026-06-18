---
name: design-shotgun
description: Generate 4-6 distinct UI/layout variants for a feature, score them against a first-run checklist, and pick one before writing the full UX spec. Use when designing a new page, view, modal, or flow. Breadth before depth.
argument-hint: "[feature name or spec path]"

---

# Design Shotgun: Parallel Variant Exploration

Generate 4-6 distinct layout directions, evaluate each against a first-run checklist, pick one, then write the full UX spec against the winner. Run it standalone when designing a new page, view, modal, or flow.

**Input:** `$ARGUMENTS` — feature name or path to a spec / `docs/prds/[feature].md`.

## Mindset (Read Before Generating Variants)

**Apply the "dumb human in 2026" lens** — imagine a distracted, AI-spoiled, first-time user with no prior context, on any device. For tariffa this is a busy clearing agent or freight forwarder who just wants to upload documents and see what will get them held at the port. Every variant must let that user understand the primary action without instruction. A clever variant that fails this scores worse than a boring variant that passes — pick the best UX, not the most ambitious one.

## Grounding

- Read the spec (or `$ARGUMENTS` block if inline)
- Read `/docs/01-product-vision.md` — the target user (freight forwarders / clearing agents) and what "done" means for v1
- Skim existing surfaces in `apps/web/app/` and `apps/web/components/` for this feature's area to avoid duplicating patterns already in use
- Respect the stack: Next.js 16 / React 19 / Tailwind CSS v4. The frontend is a thin client — variants present data and capture input; all logic lives in `apps/api`.

## Variant Generation

Produce 4-6 variants. For each, first reason through the four dimensions below, then **render it as a lo-fi greyscale wireframe** in the HTML deck (see Output). Vary along at least two of these axes:

- **Information density** — sparse editorial vs dense data grid
- **Interaction model** — static reveal vs progressive disclosure vs scroll-driven
- **Hierarchy** — headline-first vs evidence-first vs table-first
- **Animation role** — decorative vs functional (reveal-on-evidence) vs absent

Capture this for each variant (it becomes the wireframe + the right-hand meta panel):

- **Concept** — one sentence: what makes this variant distinct
- **Primary move** — the visual or interaction hook
- **Key elements** — 3-5 content blocks in reading order (these are the blocks you lay out in the wireframe)
- **Tradeoff** — what this variant gives up
- **Fits user** — which user does this serve best (e.g. high-volume clearing agent vs occasional forwarder) — pick one and justify in 1 line

**Render, don't describe.** Each variant is a fake browser window (`.screen`) whose canvas is composed from the generic wireframe kit in the template (`.field`, `.chip`/`.rail`, `.tiles`, `.segmented`, `.dropzone`, `.cards`, `table.tbl`, `.btn`, `.h-title`, `.text-line`, …). The reader should *see* the layout and reading order, not read a paragraph about it.

**Constraints:**
- **Wireframes, not production code** — no React/JSX, no real components. Greyscale building blocks only.
- **No brand colors or fonts** — the Tailwind v4 theme owns those. The template's accent blue is a neutral "this is interactive" placeholder; the green is reserved for marking the selected winner.

## Scoring

Score each variant on the four first-run checklist axes (0-3 each, 12 max):

| Axis | What to check |
|------|---------------|
| Click path | Estimated clicks to primary value. ≤3 = 3, 4-6 = 2, 7-10 = 1, >10 = 0. |
| State coverage | How cleanly empty / loading / error / offline states fit the layout. |
| Async signal fit | Whether >2s operations (extraction, classification, compliance check) have an obvious place for a progress signal. |
| Persona clarity | Whether a **dumb human in 2026** (distracted, AI-spoiled, no prior context) would understand the primary action in <3 seconds. |

Each variant's four sub-scores + total render in its right-hand meta panel (`.scoretable`), the nav pill shows the total, and **all scores are mirrored in the `#shotgun-meta` JSON block** so the result is machine-readable without scraping the rendered markup.

## Selection

- **Auto-pick** the highest total if the gap is ≥2 over the runner-up.
- **User pick** if top two are within 1 point — present both with the tradeoffs and ask.
- **Reject all + regenerate** if no variant scores ≥7 — the feature is under-specified, re-read the spec.

Record the outcome in the HTML: set `selected_variant` (and `selection_mode`: `auto` / `user` / `escalated`) in the `#shotgun-meta` block, mark the winner's `.screen` and nav pill with `class="win"` (★) and add the `Selected` tag to its header.

## Output

Write a single self-contained file: `docs/ux/[feature].variants.html`.

Build it from the template at `assets/variants-template.html` (relative to this skill) — **copy its `<style>` verbatim**, then fill in the intro, one `<section class="variant">` per variant (rendered wireframe + meta/score panel), the nav pills, and the `#shotgun-meta` JSON block. Open it in a browser to sanity-check the layouts render before declaring done.

The `#shotgun-meta` JSON island is the **machine contract** — it carries `feature`, every variant's scores, and `selected_variant`. The downstream UX write-up reads the selection from there.

After selection, write the full UX spec to `docs/ux/[feature].md` **against the winning variant only** — first-run checklist, state matrix, responsive rules.

## When to Use

- **New page / view / modal / flow** — when the layout direction is genuinely open.
- **Not for bug fixes or config changes** — only run when there's real layout exploration to do.

## What This Is Not

- Not production code — the output is a lo-fi greyscale HTML wireframe deck, never React/JSX. No real components until after selection.
- Not brand exploration — colors/fonts/spacing come from the Tailwind v4 theme. The HTML is deliberately monochrome.
- Not the full UX spec — it runs upstream of writing `docs/ux/[feature].md`, feeding it a chosen direction via `#shotgun-meta`.
