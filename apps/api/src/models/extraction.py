"""Stage 1 contract: structured data extracted from an uploaded invoice.

Produced by the extraction agent (docs/03-agent-pipeline.md) and consumed by classification. v1
scope is a single document type — a commercial invoice for a chemical/raw-material shipment
(docs/05-build-phases.md, Phase 1).

These fields mirror what's literally on the page, so they're deliberately permissive: extraction must
tolerate messy or partial real invoices and let downstream stages flag problems, rather than failing
validation at the boundary. Money is the one upgrade over the draft in docs/04-data-models.md — Decimal
instead of float, because rounding errors in a customs-value tool are not acceptable.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class LineItem(BaseModel):
    """One goods line on the invoice."""

    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_value: Decimal
    country_of_origin: str


class InvoiceExtraction(BaseModel):
    """Everything the extraction agent pulls from one commercial invoice."""

    seller: str
    buyer: str
    invoice_date: date
    currency: str
    incoterm: str
    line_items: list[LineItem]
