# Phase 2 regulatory research — source material for the knowledge base

**Retrieved: 2026-06-20.** This is a **first-pass research log**, not the finished knowledge base. It
gathers and organises what governs chemical / industrial-raw-material imports into Nigeria, so the
classification and compliance agents (Phase 2) have something concrete to ground against. Read
[`06-regulatory-knowledge-base.md`](../06-regulatory-knowledge-base.md) first — it sets the sourcing
discipline this doc follows.

> **Do not wire the compliance agent to this doc as-is.** Per the non-negotiables, every compliance
> flag must cite **official** retrieved text. Several official primary documents below could not be
> read in-session (large/binary PDFs, 403s) and are listed under "Still to obtain". Confidence is
> marked on every claim — promote a fact into the live KB only once it's ✅ official-confirmed.

**Confidence legend:** ✅ confirmed from an official primary source · 🟠 secondary source (needs
official confirmation) · ❓ not verified / conflicting / gap.

Regulations change — re-check before relying on any figure. Rates and fees especially are volatile
(see the 2025 levy churn under §1).

---

## 0. The mental model (start here)

Three bodies touch a chemical import. They divide responsibility roughly like this:

- **Nigeria Customs Service (NCS)** — applies the **tariff** (HS classification → duty band) and
  collects port charges. Drives the HS code, which everything else keys off.
- **NAFDAC** — regulates chemicals by **remit/use**: industrial & laboratory chemicals, restricted &
  agro-chemicals, precursor/controlled chemicals, plus food/pharma/cosmetic-grade. Issues **import
  permits / registration**; its e-permit reference is required on Form M.
- **SON (SONCAP)** — regulates **formulated chemical end-products** (paints, lubricants, detergents,
  fertiliser, cement…) against Nigerian Industrial Standards. **Chemicals imported as raw materials
  by bona-fide manufacturers are exempt** from offshore SONCAP (they route through a SON Import
  Permit instead).

🟠 **Key boundary:** NAFDAC and SON are mapped to **non-overlapping HS codes** — for a given HS code,
normally one of them has primary jurisdiction (source: Banwo & Ighodalo, citing the 2019 CBN/NAFDAC
circular). The exact chemical HS-code → agency map is **❓ not yet obtained** and is the most valuable
thing to nail down for the classification agent.

This three-way split is exactly what `ClassificationResult.applicable_regulator` (NAFDAC / SON / NONE)
has to decide, and what the compliance agent then checks against.

---

## 1. Tariff — NCS / ECOWAS Common External Tariff (CET)

Nigeria applies the **ECOWAS CET** with a **five-band** duty structure: **0%, 5%, 10%, 20%, 35%**
(✅ ECOWAS — ecotis.ecowas.int). Bands by intent: 0% essential/social goods; 5% raw materials &
basic goods; 10% intermediate goods; 20% finished goods; 35% specific protected goods. Most bulk
industrial chemicals sit in **5% (raw material)** or **10% (intermediate)**. 🟠 Band-per-HS-line is
inferred — **not verified against the live NCS tariff schedule** (customs.gov.ng / trade.gov.ng
returned 403/blocked in-session).

WTO MFN simple-average applied tariff for Nigeria: **12.0% (2024)** (✅ WTO ttd.wto.org).

### Chapters we care about (chemical section, HS Section VI)

- **Chapter 28 — inorganic chemicals.** Relevant headings (✅ standard HS 2022; 🟠 as applied in NG):
  `2807` sulphuric acid · `2806` hydrochloric acid · `2814` ammonia · `2815` sodium/potassium
  hydroxide (caustic soda **2815.11** solid, **2815.12** solution) · `2823` titanium oxides (pure
  TiO₂) · `2836` carbonates incl. **soda ash 2836.20**, sodium bicarbonate `2836.30`.
- **Chapter 29 — organic chemicals.** `2905` acyclic alcohols (methanol, ethanol, glycerol) · `2915`
  acetic acid/anhydride · **`2918` carboxylic acids with extra oxygen → citric acid 2918.14** ·
  `2917` phthalic/maleic anhydride.
- **Chapter 38 — miscellaneous chemical products.** `3808` insecticides/fungicides/herbicides ·
  `3811` fuel/oil additives · `3824` "chemical products & preparations not elsewhere specified"
  (catch-all formulated blends) · `3823` industrial fatty acids.

⚠️ **Classification subtlety the agent must handle (✅ form-dependent rule):** titanium dioxide is
`2823.00` as **pure** TiO₂ (Ch 28) but **`3206.11`** as a **prepared pigment ≥80% TiO₂** (Ch 32) — the
HS chapter depends on the product *form*, not the chemical name. This is exactly the kind of ambiguity
the classification agent must surface as low-confidence rather than guess.

### Port charges (the levy stack)

🟠/❓ **This regime is in active flux — treat every rate as provisional and confirm with NCS.** The
2025 timeline: the 1% **CISS** was abolished (Aug 2025) and replaced with a **4% FOB levy**, which was
then **suspended (16 Sep 2025)** pending review. Whether CISS was reinstated is ❓ unconfirmed.

| Charge | Rate | Base | Confidence |
|---|---|---|---|
| Import Duty | 0–35% (CET band) | CIF | ✅ band structure; 🟠 per-line |
| VAT | 7.5% | CIF + duty + surcharge + levies | 🟠 (rate widely cited; no increase enacted as of late-2025 sources) |
| Port surcharge | 7% of **import duty** | duty amount | 🟠 (reported still in force Aug 2025) |
| ETLS / ECOWAS levy | 0.5% | CIF (some sources say FOB) | 🟠 conflicting base |
| CISS | 1% FOB | FOB | ❓ abolished Aug 2025; status uncertain |
| 4% FOB levy (FCS) | 4% FOB | FOB | ❓ suspended Sep 2025 |

**For tariffa:** duty/levy *math* is volatile and secondary — do **not** hard-code rates into a
compliance flag yet. The durable, checkable facts are the **HS classification** and the **regulator
exposure** (below), not the naira amount.

---

## 2. NAFDAC

### Scope — broader than "food/pharma/cosmetic only"

✅ NAFDAC's statutory mandate covers "...Chemicals and Detergents" (nafdac.gov.ng functions page), and
its **Chemical Evaluation and Research (CER) Directorate** explicitly regulates **industrial and
laboratory chemicals** as a primary category (✅ nafdac.gov.ng CER directorate page). So the simple
"industrial chemicals are outside NAFDAC" assumption is **wrong** — the line is drawn by **which CER
division / pathway** applies, not by excluding industrial use.

CER divisions (✅ nafdac.gov.ng CER divisions page):

| Chemical category | NAFDAC division | Instrument |
|---|---|---|
| Industrial & laboratory chemicals | Chemical Import Control | Import permit |
| Restricted chemicals & agro-chemicals | Agro-Chemical & Restricted Chemicals | Restricted import & clearance permit |
| Ozone-depleting / chemical-weapons-adjacent | Chemical Research & Review | Convention-controlled |
| Precursor / narcotic / psychotropic | Narcotics & Controlled Substances (NCS) | NCS import permit |

🟠 **Open question (important for the agent):** whether a chemical *consumed as a pure process input*
(not sold on the market) needs a permit. The definition language ("sold or represented for domestic or
industrial use") *suggests* market-facing reach, but this is an inference — ❓ not confirmed.

### Requirements (checklist — 🟠 mostly secondary, confirm against the 2024 Regulations PDF)

Import permit (industrial/lab chemicals): CAC incorporation docs; a qualified Technical Officer
(≥OND chemistry/science); verified warehouse; **MSDS/SDS per chemical**; manufacturer's
**Certificate of Analysis**; purchase order; submitted on the Single Window portal with fee. Full
product **registration** (market-facing finished chemicals) is a heavier path (Certificate of
Manufacture & Free Sale, GMP inspection, samples, labelling) yielding a 5-year registration number.

### Form M touchpoint (✅ the concrete, checkable rule)

Since **9 Sep 2019**, only a **digital NAFDAC e-permit** is accepted for Form M. The e-permit issues an
**Approval Reference Code** that the importer enters when filing e-Form M; the portal auto-verifies it
(✅ via Banwo & Ighodalo / Mondaq reporting the CBN/NAFDAC circular). **Checkable flag:** a
NAFDAC-regulated chemical whose Form M lacks a valid e-permit reference → blocking issue.

### Precursor / controlled chemicals (✅ verified directly from nafdac.gov.ng)

Named precursor chemicals on the official NAFDAC NCS-Directorate FAQ include **ephedrine, ergotamine,
ergometrine, pseudoephedrine HCl, hydrochloric acid, sulphuric acid, methyl ethyl ketone (MEK),
toluene, acetone**. Permit processing: **max 15 working days** from a complete application.

⚠️ Several of these (**sulphuric acid, HCl, acetone, toluene, MEK**) are *everyday industrial
solvents/reagents* — so a perfectly ordinary industrial shipment can still need an **NCS precursor
permit**. This is a high-value, high-confidence rule for the compliance agent. ❓ Open: whether a
chemical that is both a general industrial chemical *and* a listed precursor needs one permit or two.

### Restricted chemicals list (🟠 retrieved but slug-mismatched — re-confirm)

A ~53-entry **Restricted Chemicals List** (dated Mar 2024) was retrieved from a nafdac.gov.ng URL whose
slug looked mismatched, so treat as 🟠 until re-fetched from the canonical page. Notable entries for
industrial importers: all **chromium / mercury / lead** compounds; **copper/zinc sulphate**;
**refrigerant gases** (R22, R134a, R600a, R407c, R410a…); **ethylene/diethylene/propylene glycol**;
**formaldehyde/paraformaldehyde**; **calcium carbide**; **ammonium nitrate/sulphate**; fertilisers
(NPK, DAP, SSP, MOP…); **urea** (noted temporarily banned).

---

## 3. SON / SONCAP

### The exemption that defines our domain (🟠 official FAQ + multiple IAFs; not re-fetched in-session)

> "Chemicals used as raw material by bonafide manufacturers... are exempted from SONCAP."

Reported consistently across the **official** SON SONCAP FAQ and multiple **authorized inspection
firms** (Cotecna, Applus+, ASC). Caveat from SON's own FAQ: *"some chemicals whose usage also extends
to other industrial purposes... are regulated by SON."* So the exemption is **use- and
importer-status-based, not purely HS-code-based** — a raw-material chemical for a certified
manufacturer is exempt from *offshore* SONCAP but still files a **SON Import Permit (IMP)**, and
"exempt from offshore SONCAP" ≠ "unregulated by SON".

🟠 The 2013 SON circular cited an exemption HS range ~`2510…`–`2942…` (≈ Chapters 25–29) **with paints
excluded** — but the list is updated periodically, so this range is likely **stale**; ❓ get the
current published list.

### Regulated chemical **end-products** (🟠 HS codes from secondary compilation)

Fertilisers (`3101–3104`), paints/varnishes (`3208–3210`), lubricating preparations (`3403`, `3811`),
brake fluids, safety matches (`3605`), cement (`2523`), gypsum (`2520`), soap & detergents (Ch 34),
tyres (`4011`). These need the full SONCAP chain.

### Documents & process (🟠 Cotecna/IAF detail; structure consistent across sources)

- **Product Certificate (PC)** — per product, required to **open Form M**. Routes **A** (unregistered,
  per-shipment, 6-mo), **B** (registered, factory-audited, 12-mo, multi-shipment), **C** (licensed,
  manufacturers). Issued by an SON-authorized inspection firm (IAF).
- **SONCAP Certificate (SC)** — **one per consignment**, required for **PAAR / customs clearance**;
  issued after Form M is approved.
- **SON Import Permit (IMP)** — the route for **exempt** raw-material/machinery imports (IMP-P opens
  Form M; IMP-S feeds PAAR).
- Chemical-specific extras: **SDS/MSDS, Certificate of Analysis**, and the NAFDAC permit where NAFDAC
  also has jurisdiction.
- Assessed against **Nigerian Industrial Standards (NIS)** (e.g. NIS 4:2017 toilet soap, NIS 5:2017
  laundry soap).

### Form M / port touchpoints (sequential — ✅ structure; 🟠 detail)

PC (or IMP-P) → **open Form M** → SC (or IMP-S) → **PAAR** → **port clearance** (NCS checks the
activated SC). No SC on a regulated good → rejection / **SONCAP default** (reported 20% of CIF or
₦2,000,000, whichever higher — 🟠).

### NSW migration (current — ✅ SON announcement, corroborated)

Effective **27 Mar 2026**, SONCAP and Import Permit processing **moved to the National Single Window
(`nsw.gov.ng`)**; the legacy `soncap.son.gov.ng` portal is superseded; a default grace window ran to
**10 May 2026**. Relevant if tariffa ever references the live filing portal.

---

## 4. What this means for the Phase 2 agents

- **Classification agent** — chapters 28/29/38 heading map above is a usable starting taxonomy. Build
  in the **form-dependent** cases (pure TiO₂ `2823` vs pigment `3206`) as known low-confidence traps,
  and emit `applicable_regulator` using §0's split.
- **Compliance agent** — the **highest-confidence, checkable rules** to ground first are: (1) NAFDAC
  **precursor permit** for listed precursors (✅), (2) NAFDAC **e-permit reference required on Form M**
  for NAFDAC-regulated chemicals (✅), (3) **SONCAP for regulated end-products** vs **raw-material
  exemption + IMP** (🟠). Each flag must cite the official text once §5 items are obtained.
- **Do not** ground compliance flags on the duty/levy *rates* yet — too volatile and unverified.

---

## 5. Still to obtain (official primary docs — promote facts to the live KB only after reading these)

1. **NAFDAC Chemical & Chemical Product Regulations 2024** (PDF on nafdac.gov.ng) — the authoritative
   definition of regulated "chemical product" and permit rules. *Single most important gap.*
2. **NAFDAC Restricted Chemicals List** — re-fetch from its canonical page to confirm the ~53 entries.
3. **SON current SONCAP regulated-product list + exemption list with 10-digit HS codes** (SON / CBN
   circular; Cotecna list is gated) — needed to map chemical HS codes → SON vs exempt.
4. **The NAFDAC ↔ SON HS-code jurisdiction map** for chemicals — drives `applicable_regulator`.
5. **Live NCS / ECOWAS CET tariff schedule** — actual duty band per chemical HS line (portal was
   blocked in-session).
6. Resolve the **port-charge regime** (CISS / 4% FOB / 7% surcharge) against a current NCS source.

These are mostly **document-fetch + read** tasks (some behind large/binary PDFs or gated downloads). A
few may need a human to download the PDF or a forwarder to confirm current practice — logged in
[`../../TODO.md`](../../TODO.md).

---

## 6. Sources

**Official (primary):**
- NAFDAC functions / mandate — https://nafdac.gov.ng/about-nafdac/nafdac-organisation/nafdac-functions/
- NAFDAC CER directorate & divisions — https://nafdac.gov.ng/about-nafdac/nafdac-organisation/directorates/chemical-evaluation-and-research/ (+ `/cer-divisions/`)
- NAFDAC NCS-directorate FAQ (precursors, 15-day timeline) — https://nafdac.gov.ng/about-nafdac/nafdac-organisation/directorates/narcotics-and-controlled-substances-ncs-directorate/narcotics-and-controlled-substances-faqs-2/ — **verified in-session**
- NAFDAC chemical imports — https://nafdac.gov.ng/chemicals/chemical-imports/
- SON SONCAP programme & FAQ — https://son.gov.ng/soncapservice/ · https://son.gov.ng/soncap-faq/ (too large to re-fetch in-session)
- SON NSW migration notice (27 Mar 2026) — https://son.gov.ng/2026/03/31/mandatory-migration-of-soncap-and-import-permit-processes-to-the-national-single-window-nsw-platform/
- National Single Window — https://nsw.gov.ng
- ECOWAS CET (five bands) — https://ecotis.ecowas.int/policy-development/common-external-tariff-cet/
- WTO tariff profile (12.0% MFN avg) — https://ttd.wto.org/en/profiles/nigeria
- NCS CET index (existence; 403 on content) — https://customs.gov.ng/?page_id=3133

**Secondary (corroborating / pointers — need official confirmation):**
- Banwo & Ighodalo (e-permit + Form M, 2019) — https://www.banwo-ighodalo.com/grey-matter/importation-of-nafdac-regulated-products-into-nigeria-now-to-be-processed-on-the-nigerian-trade-portal-with-e-permits-licenses/
- Cotecna / exports-to-nigeria.com (SONCAP routes, chemical SONCAP, exemptions) — https://www.exports-to-nigeria.com/en/services/certification-process
- Applus+ SONCAP product list — https://applus.com/global/en/what-we-do/service-sheet/soncap-certificate---nigeria
- clearingandforwardingnigeria.com (SONCAP sensitive list / exemptions, NAFDAC permit steps) — https://clearingandforwardingnigeria.com/soncap-nigeria-commodities-in-sensitive-list/
- US ITA Nigeria guides (tariffs, customs, standards) — https://www.trade.gov/country-commercial-guides/nigeria-import-tariffs
- Port-charge reporting (2025 levy changes) — Nairametrics / Daily Trend / AllAfrica (see dates inline in §1)
- HS-heading references — freightamigo.com guides (soda ash 2836.20, citric acid 2918.14, TiO₂ 2823/3206)

> Full per-source notes and the complete restricted-chemicals enumeration are preserved in the
> research-run transcript; this file is the synthesised, de-duplicated version.
