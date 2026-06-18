---
name: first-run-audit
description: Simulate a first-time user experience — identify friction, confusion, and gaps against the manual/broker status quo for a freight forwarder or clearing agent.
argument-hint: "[persona: 'clearing-agent' | 'freight-forwarder' | 'sme-importer' | 'general'] or empty for all personas"

---

# First-Run Audit: New User Experience Simulator

Simulate a first-time user arriving at tariffa. Walk through every touchpoint they'd encounter — from landing page to first completed Form M prep sheet — and evaluate the experience through the lens of someone who has never seen the product before.

**Input:** $ARGUMENTS — Optional persona to simulate. If empty, runs the general persona first, then offers to run additional personas.

**Goal:** Identify what's unclear, what's missing, what's friction, and whether a busy clearing agent would actually trust this over their current manual process or their broker.

---

## Personas

| Persona | Context | Key Questions |
|---------|---------|---------------|
| `general` | Someone who landed on the site cold | Is it obvious what this does? Can I pre-check a shipment in <5 min? |
| `clearing-agent` | Clears chemical/industrial raw-material shipments daily, time-poor | Can I catch a NAFDAC/SON issue before the port does? Faster than my spreadsheet? |
| `freight-forwarder` | Handles documentation for many importers | Can I process several shipments without re-keying everything? |
| `sme-importer` | Occasional importer, not a customs expert | Do I understand what's flagged and what to do next? (note: SME is a post-v1 layer) |

---

## Phase 1: Landing Page First Impressions (30 seconds)

**Simulate:** User lands on `/` for the first time. They have 30 seconds of attention.

Use Agent tool with `subagent_type="Explore"`:

```
Read the homepage implementation thoroughly:
1. Read the root landing page in `apps/web/app/`
2. Read ALL components referenced by the homepage (Hero, Features, HowItWorks, CTA, etc.)
3. Read any marketing copy, headlines, subheadlines
4. Check the navigation/header component for menu items
5. Check the footer for links

For each element, note:
- What text does the user actually see?
- What is the primary CTA? Is it clear?
- Is the value proposition obvious within 5 seconds?
- What questions would a new user have after reading this?
```

**Evaluate against the 5-Second Test:**

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| **What does this product do?** | | Can you explain it in one sentence from the homepage alone? |
| **Who is it for?** | | Is the target audience (forwarders / clearing agents) clear? |
| **Why should I care?** | | Is there a compelling reason to try it vs. the manual process? |
| **What do I do next?** | | Is the primary CTA obvious and compelling? |
| **Trust signals** | | Does it make clear this drafts/pre-checks and does NOT submit to NICIS/Trade Window? |

---

## Phase 2: Upload & Pre-Check Flow

**Simulate:** User clicks the primary CTA to start checking a shipment.

Use Agent tool with `subagent_type="Explore"`:

```
Read the upload / pre-check flow:
1. Read the upload page in `apps/web/app/` and all components it renders
2. Read the file upload component (react-dropzone) and the presigned-URL flow (browser → S3)
3. Read what happens after upload — how is the pipeline (extraction → classification → compliance → Form M draft) kicked off and surfaced?
4. Read any onboarding tooltips, empty states, or guided experiences
5. Note which results are shown inline vs. gated

Map the complete journey:
- Landing → Upload invoice/packing list → Pipeline runs → Review screen → Form M prep sheet
- At each step: what does the user see? What can they do? What's confusing?
```

**Evaluate:**

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| **Low-friction start** | | How quickly can I upload my first document? |
| **Time to first signal** | | How long until I see something useful (extracted data, a flag)? |
| **Async clarity** | | Do >2s operations (extraction, classification, compliance) show progress? |
| **Guided experience** | | Am I told what to do, or dropped into a blank screen? |
| **Trust** | | Is it clear the output is a draft I file myself, not an auto-submission? |

---

## Phase 3: Review Screen & Compliance Flags

**Simulate:** The pipeline finishes and the user reviews the results.

Use Agent tool with `subagent_type="Explore"`:

```
Read the review screen / results experience:
1. Read the review page in `apps/web/app/` and its main content component
2. Read how extracted line items are displayed and edited
3. Read how HS code candidates and regulator (NAFDAC/SON) classifications are surfaced
4. Read how compliance flags are presented — severity, explanation, and the regulatory citation behind each
5. Read the Form M prep sheet view/export
6. Read any empty state or first-run-specific UI

Focus on:
- Can the user understand WHY something is flagged (is the regulatory grounding visible)?
- Can they correct a wrong HS code or extracted value?
- Is it clear what action each flag requires before filing?
- How does the export/handoff to their official channel work?
```

**Evaluate:**

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| **Flag clarity** | | Is it obvious what's wrong and what to do? |
| **Grounding visibility** | | Can the user see the regulatory source behind each flag? |
| **Correctability** | | Can I fix a wrong extraction/classification without starting over? |
| **Progress feedback** | | Do I know when things are loading/saving/generating? |
| **Error recovery** | | What happens when extraction is incomplete or a check is inconclusive? |
| **Output quality** | | Does the Form M prep sheet look credible and complete? |

---

## Phase 4: Signup & Account Setup

**Simulate:** User decides to create an account after trying the product.

Use Agent tool with `subagent_type="Explore"`:

```
Read the auth and setup flow:
1. Read the signup/login pages in `apps/web/app/` and their components
2. Read what happens AFTER signup — where do they land?
3. Check for any onboarding wizard, welcome state, or getting-started flow
4. Read the main dashboard — what does a new user with 0 shipments see?
5. Look for any "import existing documents" or bulk options
```

**Evaluate:**

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| **Signup friction** | | How many fields/steps to create an account? |
| **Post-signup clarity** | | Do I know what to do after signing up? |
| **Empty state** | | What does the dashboard look like with 0 shipments? |
| **Onboarding guidance** | | Is there a walkthrough or getting-started checklist? |
| **Continuity** | | Does work I did before signing up carry over? |

---

## Phase 5: Status-Quo Gap Analysis

**Do NOT use web search.** Evaluate tariffa against what a clearing agent does TODAY based on common knowledge of the manual/broker workflow:

| Capability | Manual / broker (today) | tariffa (actual) | Gap? |
|---------|-------------------|-------------------|------|
| Extract data from invoices/packing lists | Re-keyed by hand | ? | |
| HS code classification | Agent's own knowledge / broker | ? | |
| Regulator mapping (NAFDAC, SON) | Manual lookup | ? | |
| Compliance pre-check before port | Often caught only at the port | ? | |
| Regulatory grounding for each flag | Tribal knowledge | ? | |
| Form M prep | Manual spreadsheet / broker | ? | |
| Speed for repeat shipments | Slow, repetitive | ? | |

### What Would Make Someone Switch?

Based on the codebase analysis, identify tariffa's **unique value**:
- What does tariffa catch that the manual process misses until the port?
- Is the regulatory grounding (RAG) visible and trustworthy to a skeptical agent?
- Are there features that are built but not surfaced well?

---

## Phase 6: Friction Log & Recommendations

Compile all findings into a structured report.

### Friction Log Format

For each friction point found:

```markdown
### [F-XX] [Short description]
- **Phase:** [1-5]
- **Severity:** P0 (blocker) | P1 (significant) | P2 (annoyance) | P3 (nice-to-have)
- **User impact:** [What the user experiences]
- **Expected:** [What they expected to happen]
- **Actual:** [What actually happens]
- **Recommendation:** [Specific fix]
- **Status-quo pressure:** [Does the manual/broker process handle this better?]
```

### Report Structure

Save the report to `docs/audits/first-run-audit-{persona}-{date}.md`:

```markdown
# First-Run Audit: {Persona} — {Date}

## Executive Summary
- **Overall Score:** X/50 (sum of all phase scores)
- **Would a {persona} switch from their current process?** Yes/No/Maybe — [why]
- **Time to first useful signal:** [estimated clicks/seconds]
- **Top 3 wins:** [things that already work well]
- **Top 3 blockers:** [things that would stop adoption]

## Phase Scores
| Phase | Score | Key Issue |
|-------|-------|-----------|
| Landing Page | /25 | |
| Upload Flow | /25 | |
| Review Screen | /30 | |
| Signup & Setup | /25 | |
| Status Quo | N/A | |

## Detailed Friction Log
[All F-XX items, sorted by severity]

## Status-Quo Position
[Gap analysis summary]

## Recommended Actions
### Quick Wins (< 1 day each)
1. ...

### Medium Effort (1-3 days)
1. ...

### Strategic (requires planning)
1. ...

## What's Actually Great
[Highlight what works — these are the foundation to build on]
```

---

## Phase 7: Present & Next Steps

Present the report summary and offer:

1. **Run another persona** — Simulate a different user type
2. **Deep-dive a specific phase** — Focus on one area (e.g., just the review screen)
3. **Generate a PRD** — Turn top recommendations into a PRD under `docs/prds/`
4. **Create tasks** — Turn quick wins into an immediate TODO list

---

## Critical Rules

- **Be brutally honest** — Sugarcoating defeats the purpose. If the landing page is confusing, say so.
- **Think like a real user, not a developer** — Clearing agents don't read code. They see buttons, text, and outcomes.
- **Every criticism needs a recommendation** — Don't just identify problems, propose solutions.
- **Acknowledge what works** — The audit should also highlight strengths.
- **Compare fairly** — The manual/broker process is entrenched and trusted. Frame gaps realistically.
- **Focus on switchability and trust** — The core question is: "Would a skeptical agent trust this enough to rely on it before filing?"
- **Read the actual UI text** — Don't infer from component names. Read the actual copy users see.
- **Check that the "drafts only, never submits" boundary is clear** — this is a product non-negotiable.
- **Check mobile responsiveness** — Look at responsive styles/breakpoints (Tailwind v4) in components.

---

## Usage Examples

```
/first-run-audit                     # General persona (default)
/first-run-audit clearing-agent      # Daily clearing agent pre-checking shipments
/first-run-audit freight-forwarder   # Forwarder processing many importers' docs
/first-run-audit sme-importer        # Occasional importer (post-v1 layer)
```

---

## When to Use

- **Before a launch or major release** — Sanity-check the new user experience
- **After significant UI changes** — Verify nothing broke in the user journey
- **When activation is low** — Diagnose where users are dropping off
- **When planning the roadmap** — Understand gaps vs. the manual process to prioritize features
