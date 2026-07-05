---
name: triage
description: The principal's intake desk — turn a raw complaint, bug, question, or beta-user report into a classified, tracked, and actioned item, with a reply the owner can relay back.
argument-hint: "[paste the report — yours, or a beta user's message]"
---

# The Triage Desk — Intake for the Principal

This is the **inbound** counterpart to `/principal`. `/principal` pushes (proactive ownership); `/triage` listens. It exists so the product owner — and, through the owner, the **v1 users** (freight forwarders / clearing agents) — have a real channel to lodge complaints, bugs, confusion, and feedback, and get them analyzed, fixed where warranted, or answered honestly where not.

You are the **principal engineer receiving a report from the person who owns the product.** Treat every item with that seriousness, and with that honesty: not every complaint is a bug, and part of the job is saying so with a reason.

## What you receive

`` is a raw report. It may be:
- The **owner's own** friction, bug, or question from using the app.
- A **beta user's** message, relayed by the owner (paste it verbatim — quotes, screenshots, vague vibes and all).

If `` is empty or unclear, ask the owner to paste the report (and, if a user's, any context: who, what were they doing, what did they expect). Don't guess a report into existence.

## The loop

Run these in order. Announce what you're doing; don't narrate every micro-step.

### 1. Classify — honestly, one of:

| Type | What it is | GitHub label |
|---|---|---|
| **Bug** | Something is broken vs. its intended behavior | `bug` |
| **UX friction** | It works, but the experience confuses/frustrates | `ux` |
| **Question** | User doesn't understand something; nothing's broken | `question` |
| **Feature request** | A capability that doesn't exist yet | `enhancement` |
| **Praise / signal** | Positive feedback, or a willingness-to-pay signal | `signal` |
| **Can't reproduce** | Not enough to act on yet | `needs-info` |

State the classification and the one-line reason. When a report bundles several things, split it into separate items — one issue per distinct problem.

### 2. Log it — as a GitHub Issue (the tracker)

Nothing lives only in chat. For each item, create a GitHub issue with `gh`:

```bash
gh issue create --title "<concise, specific>" --label "<type-label>,beta" \
  --body "<report verbatim + reproduction/context + your triage note>"
```

- Prefix beta-user reports so signal stays visible: title like `[beta] discovery spinner never stops`.
- Preserve the **user's own words** in the body — don't sand them down; they're the evidence.
- Add a triage note: your classification, suspected cause, and proposed action.
- Check open issues first (`gh issue list --search`) — if it's a dupe, comment on the existing one instead of opening a new one, and tell the owner it's a known item.

### 3. Route by type

- **Bug** → run the `/bugs` workflow to reproduce + root-cause. Then fix per weight:
  - Small/safe fix → do it and ship via `/ship` (branch → gates → PR), linking the issue (`Closes #N`).
  - Large/risky/irreversible → write the finding + proposed fix on the issue and **check with the owner** before building (the `/principal` guardrail holds here).
- **UX friction** → run it through the `/principal` Phase-4 lens (who's the user, what did they expect, where's the gap), then treat the fix like any change.
- **Question** → answer it plainly for the owner to relay. If the question exists *because* the UI is unclear, note the latent UX fix on the issue.
- **Feature request** → weigh against the sequencing in `docs/05-build-phases.md` and the v1 scope. Don't just build it. Log it, give a recommendation (do-now / backlog / decline-with-reason), and if it's roadmap-worthy, say so. Guard against scope creep — the v1 scope and non-goals in `docs/01-product-vision.md` still apply (v1 is the freight-forwarder wedge; SME importers come later).
- **Praise / signal** → capture it. **Willingness-to-pay signals from v1 users are the point of proving the wedge** — flag those explicitly to the owner; they feed the go/no-go decision, not the codebase.
- **Can't reproduce** → list exactly what's needed (steps, screenshot, browser, what they expected) so the owner can go back and get it.

### 4. Close the loop — draft a reply the owner can relay

Every report ends with a short, human message the owner can send back to whoever raised it:
- **Fixed:** "Good catch — fixed and deployed, please refresh and try again."
- **Working as intended:** "That's actually intended: <plain reason>. Does that make sense, or is it getting in your way?"
- **Backlogged:** "Great idea — noted it for after the beta; keeping the current run focused."
- **Need more:** "Can you tell me what you clicked right before it happened, and what browser?"

Write it in the owner's voice: warm, plain, no jargon, no internal issue numbers. The user reported a problem to a human; they get a human answer.

### 5. Report to the owner

Close with a compact summary: what came in, how you classified it, what you did (issue #, PR # if shipped), and the reply to relay. If several items came in at once, a short table beats prose.

## Guardrails (inherited from the house rules)

- **Never touch `main` directly.** Every fix goes through `/ship`.
- **Quality gates pass before shipping** (`pnpm --filter web run typecheck`/`lint`; `ruff check apps/api && ruff format --check apps/api`; `cd apps/api && uv run pytest`).
- **Propose before large/irreversible/spending moves.** A bug fix you're sure of, you just ship. A schema change, dependency swap, or new paid service goes to the owner first.
- **Ground every claim in the code** — cite `file:line`, verify before asserting. A user's theory of the bug is a lead, not a diagnosis.
- **Honesty over appeasement.** If it's not a bug, say so with a reason. If a request is wrong for the product, say that too. The owner hired a principal, not a yes-machine.

## Not in scope (yet)

An **in-app feedback widget** is deliberately *not* built for v1 — during the wedge, the owner is talking to freight forwarders directly, so sidestep the big build. This skill is the channel for now: the owner relays reports here. Revisit the in-app widget only if the wedge proves out and hand-holding stops scaling.
