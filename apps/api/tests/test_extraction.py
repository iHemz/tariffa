"""Tests for the extraction agent.

The wiring tests use pydantic-ai's TestModel so they run with no API key and no network — they prove
the agent is plumbed to the right output type and that the media-type guard holds. The live
golden-case test is a scaffold: it runs only when ANTHROPIC_API_KEY is set and a real sample invoice
is dropped at tests/fixtures/sample_invoice.pdf, which is the actual Phase 1 quality bar.
"""

import os
from pathlib import Path

import pytest
from pydantic_ai.models.test import TestModel

from src.agents.extraction import (
    UnsupportedDocumentError,
    extract_invoice,
    get_extraction_agent,
)
from src.models import InvoiceExtraction


async def test_rejects_an_unsupported_document_media_type() -> None:
    # Guard runs before any model call, so this needs no API key.
    with pytest.raises(UnsupportedDocumentError):
        await extract_invoice(b"plain text, not a document", "text/plain")


async def test_returns_a_validated_invoice_extraction(monkeypatch) -> None:
    # Constructing the agent needs *a* key; TestModel means no real call is made.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    get_extraction_agent.cache_clear()

    agent = get_extraction_agent()
    with agent.override(model=TestModel()):
        result = await extract_invoice(b"%PDF-1.7 fake bytes", "application/pdf")

    assert isinstance(result, InvoiceExtraction)


async def test_accepts_images_as_well_as_pdfs(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    get_extraction_agent.cache_clear()

    agent = get_extraction_agent()
    with agent.override(model=TestModel()):
        result = await extract_invoice(b"fake png bytes", "image/png")

    assert isinstance(result, InvoiceExtraction)


_SAMPLE_INVOICE = Path(__file__).parent / "fixtures" / "sample_invoice.pdf"


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") or not _SAMPLE_INVOICE.exists(),
    reason="live golden-case needs ANTHROPIC_API_KEY and tests/fixtures/sample_invoice.pdf",
)
async def test_extracts_key_fields_from_a_real_invoice() -> None:
    # The riskiest stage: this is where extraction quality on real formatting gets measured.
    # Rebuild so we use the real key, not a dummy one a wiring test may have cached.
    get_extraction_agent.cache_clear()
    result = await extract_invoice(_SAMPLE_INVOICE.read_bytes(), "application/pdf")

    assert result.seller
    assert result.buyer
    assert result.line_items, "expected at least one goods line"
