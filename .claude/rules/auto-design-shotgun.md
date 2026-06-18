# Auto-Design-Shotgun for New UI Features

When I start designing a **new user-facing feature, page, view, or flow** in `apps/web`, **automatically invoke `/design-shotgun`** before writing any UX spec or JSX. Don't ask whether I want variants — explore breadth first, then converge.

## Trigger Signals

Auto-invoke `/design-shotgun` when the request matches ANY of these patterns:

1. **"Design / build / let's create [a new screen / page / view / dashboard / modal / flow]"** — net-new UI surface (e.g. the upload screen, the review screen, the Form M prep sheet)
2. **"How should the [feature] UI look / be laid out"** — layout is undecided
3. **"I want a [feature] that does X"** where X clearly needs a new visual surface and no layout has been chosen
4. **A spec or feature description arrives** (e.g. from `/docs/`) and the next step is UX/layout
5. **A net-new component or surface** under `apps/web/` where no layout has been chosen yet

The point: when layout direction is genuinely open, generate 4–6 scored variants and pick one **before** committing to a single design.

## DO NOT auto-invoke when:

- The change is a **bug fix, copy change, or config change** — no new layout decision
- The layout already exists and I want an edit ("move the button", "add a column")
- I reference an existing component to extend ("make the review table also show X")
- A Figma design or chosen variant already exists for this feature
- I explicitly say "quick", "just implement", or hand you a finished spec
- Backend-only work in `apps/api` with no visual surface

When unsure whether a layout decision is still open, ask one short question rather than running the shotgun blindly.

## How to invoke

Pass the feature name or spec path as the argument:

```
/design-shotgun "[feature name or /docs/[spec].md]"
```

The skill writes a lo-fi wireframe deck (variants + score panels) with an embedded `#shotgun-meta` JSON block naming the selected variant. The downstream `/ux-design` step then writes the full spec **against the selected variant only**.

## Why

Jumping straight to a single layout locks in the first idea before its tradeoffs are visible. Generating and scoring 4–6 variants against the First-Run Checklist surfaces the click-path, state-coverage, and persona-clarity problems while they are still cheap to fix — breadth before depth. This mirrors `auto-investigate.md`: a known-good multi-step skill should run automatically for the situations it was built for, not wait to be remembered.
