"""Stage 3 contract: compliance flags raised against the classified goods.

Produced by the compliance agent (docs/03-agent-pipeline.md). Every flag MUST cite the retrieved
regulatory text it came from — a flag without a citation is not meaningfully different from a guess
and undermines the whole premise of the tool (see the non-negotiables in CLAUDE.md).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.common import OverallStatus, Severity


class ComplianceFlag(BaseModel):
    """A single issue the compliance agent raised."""

    severity: Severity
    message: str
    cited_rule: str
    """The specific regulation / retrieved source text this flag is grounded in. Required."""

    related_line_item_index: int | None = Field(default=None, ge=0)
    """Index into InvoiceExtraction.line_items, or None for shipment-level flags."""


class ComplianceReport(BaseModel):
    """All flags for one shipment plus the roll-up verdict."""

    shipment_id: str
    flags: list[ComplianceFlag]
    overall_status: OverallStatus
