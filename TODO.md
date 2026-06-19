# tariffa — backlog

A living list of work that's **deferred, blocked, or needs real-world resources** — so we can keep
building without losing track. Revisit at your convenience.

How we use this:
- When something needs you (credentials, a decision, a real document) or external research, it goes
  here instead of blocking the build.
- Claude can pick up the **"Claude can do"** items anytime — just say the word.
- Keep entries short: what's needed, why it matters, who can do it.

Status keys: 🔴 blocked on you · 🟡 Claude can research/start · 🟢 ready to build · ✅ done

---

## Blocked on you (credentials / real-world resources)

- 🔴 **Real sample invoices for the extraction golden set.** The synthetic fixture is clean digital
  text — the easy case. Extraction is the riskiest stage; real quality is unmeasured until we run it
  against genuine **scanned / phone-photographed** commercial invoices for chemical shipments, with
  varied formatting. Drop them at `apps/api/tests/fixtures/sample_invoice.pdf` (and add more cases).
  Best source: a clearing agent / forwarder (also doubles as early user contact). Claude can find
  public *filled-example* links (see below) but generally can't pull binary PDFs into the repo.

- 🔴 **Postgres + pgvector provisioning** (Railway or Fly.io) → set `DATABASE_URL` in
  `apps/api/.env`, run `CREATE EXTENSION IF NOT EXISTS vector;`, then we add a minimal `shipments`
  table. Phase 0's 4th bullet, still open. Unblocks persistence + the compliance RAG store.

- 🔴 **S3 bucket + AWS credentials** for the browser → S3 presigned-upload flow (`S3_BUCKET`,
  `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` in `apps/api/.env`). Needed before the real upload UI.

- ✅ **`ANTHROPIC_API_KEY`** — set; live extraction round-trip verified.

## Research Claude can do (just ask)

- 🟡 **Find public "filled commercial invoice" examples** (links) for chemical shipments to seed the
  golden set — carriers (DHL/Maersk/Flexport) and supplier sample docs. I'll collect URLs here; you
  download the ones you like.

### Phase 2 regulatory research — first pass DONE ✅

Synthesised into [`docs/regulatory/phase2-research.md`](docs/regulatory/phase2-research.md) (NCS/CET
tariff chapters 28/29/38, NAFDAC, SON/SONCAP — with confidence levels + citations). Verified directly:
NAFDAC controls common industrial precursors (sulphuric acid, HCl, acetone, toluene, MEK). Remaining
follow-ups to harden it into the live KB:

- 🔴 **NAFDAC Chemical & Chemical Product Regulations 2024 (PDF)** — the authoritative permit rules;
  the PDF is binary and wasn't readable in-session. *Most important gap.* May need you to download it.
- 🔴 **SON current SONCAP regulated + exemption product list with 10-digit HS codes** — the official
  list / CBN circular is binary; the Cotecna copy is behind a gated download. Map chemical HS codes →
  SON-regulated vs exempt.
- 🟡 **NAFDAC ↔ SON HS-code jurisdiction map for chemicals** — drives `applicable_regulator`. I can
  keep digging; may ultimately need the two lists above.
- 🟡 **Live NCS / ECOWAS CET tariff schedule** — actual duty band per chemical HS line (portal was
  403-blocked in-session). Re-confirm the NAFDAC Restricted Chemicals List from its canonical page too.
- 🟡 **Port-charge regime** (CISS / 4% FOB / 7% surcharge) — resolve against a current NCS source;
  it churned through 2025 and is unsettled.

## Deferred code decisions

- 🟢 **Structured party fields.** `InvoiceExtraction.seller` / `buyer` currently capture the full
  name+address block as one string. Revisit when building the Form M prep sheet (Phase 3), which will
  need structured importer/supplier details — likely a `Party` model (name + address). Not blocking
  anything now.
- 🟢 **Auto-load `.env` in tests.** Consider `pytest-dotenv` or a `conftest.py` `load_dotenv()` so the
  live golden-case picks up `apps/api/.env` without manually sourcing it.

## Verification not yet done

- 🟢 **Browser round-trip of the Phase 0 page.** Now that the key is set, click "Run agent" on the
  home page and confirm `/ping` returns through the UI (only the headless round-trip is verified).

---

## Phase map (from `docs/05-build-phases.md`)

- **Phase 0 — skeleton:** ✅ code done · DB + S3 provisioning still open (above).
- **Phase 1 — extraction agent:** ✅ agent built & verified on synthetic invoice · 🔴 real-document
  quality open (needs sample invoices above).
- **Phase 2 — classification + compliance:** 🟡 regulatory research first pass done
  (`docs/regulatory/phase2-research.md`); a few official docs still to obtain (above) before grounding
  the compliance agent. Then build the classification + compliance agents.
- **Phase 3 — form drafting + review UI:** not started.
- **Phase 4 — polish + real forwarder trials:** not started.
