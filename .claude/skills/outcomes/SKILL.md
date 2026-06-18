---
name: outcomes
description: Interactive project setup to discover outcomes and write a deliverable-definition doc that downstream specs build on.
argument-hint: "[optional outcome description]"

---

# Outcomes: Define Project Deliverables

Interactive project setup — discover the outcomes I'm committing to and capture them in a single deliverable-definition doc that PRDs and other specs build on.

**Input:** $ARGUMENTS — Optional outcome description to seed the conversation

## Steps

### 1. Idempotency Gate

Check if `docs/OUTCOMES.md` exists:
- **If exists:** Offer to review/update, start fresh, or cancel
- **If missing:** Proceed to discovery

### 2. Interactive Discovery

**Round 1:** One open question — describe the project, who it's for, what success looks like.

**Round 2:** Extract deliverables, propose as outcomes with success criteria. Max 3 questions.

**Round 3: Design References**
Ask: "Do you have Figma designs for any of these outcomes? Provide the Figma URL(s) (figma.com/design/...) for each outcome that has one, or say 'none'."
- Validate URL format: must match `figma.com/design/:fileKey/...` or `figma.com/make/:fileKey/...`
- If no URL provided, store `figma_url: none` on the outcome
- If URL provided, store `figma_url: <url>` on the outcome

**Round 4+:** Refinement only if contradictions, vague criteria, or unclear dependencies.

**Stop when:** Each outcome is one sentence, has measurable criteria, no contradictions, dependencies documented.

### 3. Confirmation

Present outcome table and wait for my explicit confirmation.

### 4. Write the Outcomes Doc

- Create/overwrite `docs/OUTCOMES.md` with outcomes, criteria, constraints, non-goals
- Include `figma_url: <url>` (or `figma_url: none`) as metadata on each outcome that has a design reference

### 5. Completion Summary

Report the file written and which outcomes are now defined.
