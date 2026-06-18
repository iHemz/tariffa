"""Stage 2 contract: an HS-code classification for one extracted line item.

Produced by the classification agent and consumed by the compliance agent (docs/03-agent-pipeline.md).
One ClassificationResult per line item; `line_item_index` points back into
InvoiceExtraction.line_items.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.common import Regulator


class ClassificationResult(BaseModel):
    """The agent's HS-code call for a single line item."""

    line_item_index: int = Field(ge=0)
    hs_code_candidate: str
    confidence: float = Field(ge=0.0, le=1.0)
    """0-1. Surface low-confidence results to the reviewer rather than guessing."""

    applicable_regulator: Regulator
    reasoning: str
    """Short explanation — lets the human reviewer trust or override the call."""
