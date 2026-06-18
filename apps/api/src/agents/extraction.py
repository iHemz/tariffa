"""Extraction agent — Stage 1 of the pipeline.

Reads an uploaded commercial invoice (PDF or image) and returns a typed `InvoiceExtraction`
(docs/03-agent-pipeline.md, docs/04-data-models.md). Claude reads PDFs and images natively, so the
document is sent straight to the model with a structured output schema — no separate OCR step
(add one later only if extraction quality on real documents proves it's needed).

This is the riskiest stage in the project: extraction quality varies a lot with document formatting.
The design here is deliberately single-pass and faithful — the agent transcribes what is on the page
and never invents values; downstream review and the compliance stage catch the rest.

Requires ANTHROPIC_API_KEY at run time (pydantic-ai bundles the Anthropic provider). The agent is
built lazily so this module — and the app — still import without a key.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_ai import Agent, BinaryContent

from src.models import InvoiceExtraction

# Media types Claude can read natively. Anything else should be rejected before we spend a model call.
SUPPORTED_MEDIA_TYPES: frozenset[str] = frozenset(
    {"application/pdf", "image/png", "image/jpeg", "image/webp"}
)

EXTRACTION_SYSTEM_PROMPT = """\
You extract structured data from a single commercial invoice for a chemical or industrial \
raw-material shipment into Nigeria. You work for a freight forwarder preparing import \
documentation.

Transcribe only what is actually on the document:
- Pull the seller, buyer, invoice date, currency, incoterm (e.g. CIF, FOB), and every goods line.
- For each line item, capture the description exactly as written, the quantity and its unit, the \
unit price, the line total, and the country of origin.
- Use the currency and values printed on the invoice. Do not convert currencies or recompute totals.

Be faithful, not creative:
- Never invent, guess, or infer a value that is not present. If a field is genuinely not on the \
document, leave it blank rather than fabricating it.
- Do not normalise or "clean up" descriptions — a clearing agent needs the original wording to \
classify the goods.
- Do not add commentary, assumptions, or fields that were not requested.
"""


@lru_cache(maxsize=1)
def get_extraction_agent() -> Agent[None, InvoiceExtraction]:
    """Build the extraction agent lazily (see module docstring for why)."""
    return Agent(
        "anthropic:claude-opus-4-8",
        output_type=InvoiceExtraction,
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
    )


class UnsupportedDocumentError(ValueError):
    """Raised when an uploaded document is not a media type Claude can read."""

    def __init__(self, media_type: str) -> None:
        self.media_type = media_type
        super().__init__(
            f"Unsupported document media type {media_type!r}; "
            f"expected one of {sorted(SUPPORTED_MEDIA_TYPES)}."
        )


async def extract_invoice(document: bytes, media_type: str) -> InvoiceExtraction:
    """Extract a commercial invoice from raw document bytes.

    Args:
        document: the raw file bytes (PDF or image).
        media_type: the document's MIME type, e.g. "application/pdf".

    Raises:
        UnsupportedDocumentError: if `media_type` is not one Claude can read.
    """
    if media_type not in SUPPORTED_MEDIA_TYPES:
        raise UnsupportedDocumentError(media_type)

    result = await get_extraction_agent().run(
        [
            "Extract the commercial invoice in this document.",
            BinaryContent(data=document, media_type=media_type),
        ]
    )
    return result.output
