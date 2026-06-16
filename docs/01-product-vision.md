# Product vision

## The problem

Nigerian importers and freight forwarders deal with a customs documentation process that is notoriously easy to get wrong: Form M, PAAR, HS code classification, and the certificates required by NAFDAC and SON depending on the product category. A single mistake or missing document can mean a shipment sits at port for weeks, which is expensive in both money and time. Freight forwarders currently catch these errors manually, if at all, after submission.

## Why this, why now

Nigeria's AI startup landscape has grown past 120 active startups, but the concentration is heavily in fintech, health tech, agriculture, and language technology. Trade compliance and customs documentation is comparatively untouched — which makes it a credible, differentiated space rather than another entrant into an already crowded category.

## Target user

**v1 (the wedge): freight forwarders and customs clearing agents.** They process shipments repeatedly, so the value of catching an error before submission compounds across every shipment they handle. They're also positioned to give fast, specific feedback, which matters more at this stage than reaching the largest possible audience.

**Later: SME importers**, self-serve, reusing the same agent pipeline behind a simplified UI once it's proven with the professional users.

## Vertical for v1

Chemicals and industrial raw materials. This is a deliberate narrowing, not a limitation — it lets the regulatory knowledge base stay tractable (a handful of HS code chapters and a known set of regulators) instead of trying to cover every import category at once. Additional categories (electronics, building materials under SON) can be added once the pipeline is proven here.

## What "done" looks like for the MVP

A user uploads a commercial invoice and packing list for a chemical/raw-material shipment. The system:

1. Extracts structured data from the documents.
2. Classifies the line items against HS codes and determines which regulators apply.
3. Cross-checks the data against real regulatory requirements and flags anything missing, inconsistent, or risky — with a citation to which rule triggered the flag.
4. Drafts a Form M prep sheet from the validated data.
5. Presents all of this in a review screen where the user can edit fields before exporting.

## Explicit scope boundary

This tool does not submit anything to NICIS, Trade Window, or any other government system — that requires official accreditation this project doesn't have and shouldn't pretend to have. The output is a pre-clearance compliance copilot: it produces a correct, error-checked draft that the user or their licensed broker files through the official channel. This is an honest scope, and it's a stronger pitch than overclaiming an integration that doesn't exist: "we cut your document prep time and error rate" is real and demonstrable.

## Success signal for the portfolio piece

Not "the code runs." The bar is: a real freight forwarder, shown 2-3 realistic example shipments running through the full pipeline, says this would have caught something or saved them time. That's the difference between a demo and evidence of product judgment.
