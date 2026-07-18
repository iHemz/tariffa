# Tariffa — Plays

**What it is:** an AI import-compliance agent for Nigerian freight forwarders and clearing
agents. It extracts structured data from invoices and packing lists, classifies goods against
HS codes and the right regulators (NAFDAC, SON), flags compliance issues before they cause port
delays, and drafts a Form M prep sheet. It drafts, it does not submit: the human files through
the official channel (NICIS / Trade Window).
**Stage:** monorepo (apps/web Next.js thin client, apps/api FastAPI + Postgres + S3 + Claude).

**Through-line (shared across my products):** grounded, honest AI that shows its work and
never fakes authority. Tariffa flags for a human expert and cites the rule; it never pretends
to have filed anything. In a regulated domain, that honesty is the product, not a caveat.

**How to use:** from this repo's Claude Code session, say "run the product play"
(or "career play" / "audience play"). Read that section, do the next unchecked step, then
update its Status line.

---

## Product play

**Thesis.** Clearing agents and importers lose real money to port delays and demurrage caused
by paperwork errors: wrong HS codes, missed NAFDAC/SON requirements, weak Form M prep. Tariffa
pre-checks the docs and tells you what will get flagged at the port, before the shipment gets
there. They pay because one avoided delay is worth more than a year of subscription.

**ICP.** Clearing and forwarding agents, freight forwarders, and import-heavy SMBs in the
initial niche (chemicals and industrial raw materials). Start narrow where the rules are
strict and the penalty for error is highest, then broaden goods categories.

**Wedge → expansion.**
- Wedge: "pre-check my docs and tell me what will get flagged."
- Then: HS-code classification assistant, regulator-requirement checker, Form M prep, then
  landed-cost/duty estimation and document generation. Stay a prep layer; do not become a filer.

**Pricing.** Per-shipment fee (per pre-check / Form M draft) or a volume subscription for busy
agents. Price against demurrage saved: willingness to pay is high because the alternative is
paying storage/demurrage by the day. Higher ACV than a consumer tool.

**Moat / honesty angle.** Two moats. First, encoded domain knowledge (HS codes, NAFDAC/SON
rules) that generic AI cannot do reliably and that compounds as you add categories. Second, the
"prep not submit" safety design and rule citations, which build trust in a domain where a
confident wrong answer costs money. Keep rules current and always cite the source.

**Distribution.** Design-partner a few clearing agents, then work the associations and
freight-forwarding networks. It is a tight-knit industry; word of mouth and a couple of
"caught a costly error" stories travel fast.

**Watch-outs.** Regulatory accuracy is existential. Frame as an assistant that flags for a
human expert. Cite the rule behind every flag. Version and date the rule set.

**Metrics to capture.** Compliance issues caught pre-port, HS-classification accuracy on real
docs, time saved per shipment, demurrage avoided (turn these into case studies).

**Next steps.**
- [ ] Nail HS classification + regulator flagging accuracy on a batch of real invoices/packing lists
- [ ] Ship the Form M prep-sheet draft quality
- [ ] Pilot with 2-3 clearing agents; instrument the metrics above
- [ ] Add rule citations + a dated rule-set version to every flag

**Status:** _not started_

---

## Career play

**The story it tells.** "I built a vertical AI agent that encodes real regulatory domain
knowledge to save importers money." The un-sexy, high-value B2B AI that actually gets paid for.
Shows hard domain modelling + agent orchestration + clean architecture.

**Positioning line.** "AI engineer who builds grounded, domain-heavy vertical agents for real
B2B pain."

**Case-study + interview ammo (`/work/tariffa`).** The strict client/server separation (web
never touches Postgres, S3, or Claude directly); the HS-code classification approach; grounding
regulatory rules with citations; the "prep not submit" safety design; extracting structured data
from messy invoices and packing lists. Strong for AI-agent / vertical-SaaS / fintech-adjacent
roles.

**Where to deploy.** Portfolio, LinkedIn, YC (Africa / logistics / vertical-AI angle), Djinni.

**Next steps.**
- [ ] Capture accuracy numbers + one pilot testimonial
- [ ] Write the case study; add to portfolio PROJECTS + resume
- [ ] Add a "vertical AI, boring moat" line to the pitch bank

**Status:** _not started_

---

## Audience play

**Narrative.** "Vertical AI where the moat is boring domain knowledge, not the model." Plus:
"building AI for African trade and logistics." High-credibility, low-competition niche.

**Hooks.**
- "AI won't fix Nigerian port delays. Regulation-aware, grounded AI might. Here's what I'm
  building."
- "The hardest part of my import-compliance AI is that it must never pretend to be sure about a
  NAFDAC rule."
- Teardown of an HS-code misclassification that would cost real money.

**Angles.** Doc-in → flags-out demo; "what actually gets flagged at the port" explainers; the
prep-not-submit safety stance; the domain-knowledge-as-moat thesis (the AI-builder crowd loves
this); pilot results.

**Channels + cadence.** LinkedIn (Nigerian business + AI-builder audience), X for the
vertical-AI thesis, relevant trade/logistics communities. Weekly + pilot milestones.

**Assets to produce.** Doc-in/flags-out demo clip, HS-classification example, a "demurrage
saved" case-study card.

**Next steps.**
- [ ] Post #1: the thesis (vertical AI + boring moat + real money) with a pre-check demo
- [ ] "What gets flagged at the port" explainer series
- [ ] Milestone post when a pilot catches a real, costly error

**Status:** _not started_
