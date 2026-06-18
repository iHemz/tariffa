"""Stage 4 contract: the drafted Form M prep sheet.

Produced by the form-drafting agent (docs/03-agent-pipeline.md). This is a DRAFT only — tariffa never
submits to NICIS, Trade Window, or any government system on the user's behalf (CLAUDE.md
non-negotiables). `form_type` reflects that: it's a prep sheet, not a filing.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class FormDraft(BaseModel):
    """Pointer to a generated Form M prep-sheet document."""

    shipment_id: str
    form_type: str = "Form M prep sheet"
    pdf_url: str
    generated_at: date
