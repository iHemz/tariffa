"""Contract tests for the pipeline data models.

Each test states an invariant the typed boundary must enforce, not just an observed behavior.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models import (
    ClassificationResult,
    ComplianceFlag,
    InvoiceExtraction,
    LineItem,
    OverallStatus,
    Regulator,
    Severity,
)


def _line_item(**overrides) -> dict:
    base = {
        "description": "Sodium hydroxide flakes",
        "quantity": "100",
        "unit": "bag",
        "unit_price": "12.50",
        "total_value": "1250.00",
        "country_of_origin": "China",
    }
    return {**base, **overrides}


def test_monetary_fields_parse_as_decimal_not_float() -> None:
    item = LineItem(**_line_item())
    assert isinstance(item.unit_price, Decimal)
    assert isinstance(item.total_value, Decimal)
    # exact value preserved — the reason we use Decimal over float
    assert item.total_value == Decimal("1250.00")


def test_classification_rejects_confidence_above_one() -> None:
    with pytest.raises(ValidationError):
        ClassificationResult(
            line_item_index=0,
            hs_code_candidate="2815.11.00",
            confidence=1.5,
            applicable_regulator=Regulator.NAFDAC,
            reasoning="caustic soda",
        )


def test_classification_rejects_negative_confidence() -> None:
    with pytest.raises(ValidationError):
        ClassificationResult(
            line_item_index=0,
            hs_code_candidate="2815.11.00",
            confidence=-0.1,
            applicable_regulator=Regulator.SON,
            reasoning="caustic soda",
        )


def test_compliance_flag_requires_a_cited_rule() -> None:
    # cited_rule has no default — a flag without a citation must not validate.
    with pytest.raises(ValidationError):
        ComplianceFlag(
            severity=Severity.BLOCKING, message="Missing NAFDAC registration"
        )


def test_compliance_flag_defaults_to_shipment_level() -> None:
    flag = ComplianceFlag(
        severity=Severity.WARNING,
        message="HS code is low confidence",
        cited_rule="NCS Tariff, Chapter 28",
    )
    assert flag.related_line_item_index is None


def test_invoice_requires_a_valid_date() -> None:
    with pytest.raises(ValidationError):
        InvoiceExtraction(
            seller="Acme Chemicals Ltd",
            buyer="Lagos Importers Co",
            invoice_date="not-a-date",
            currency="USD",
            incoterm="CIF",
            line_items=[LineItem(**_line_item())],
        )


def test_enums_expose_stable_wire_values() -> None:
    # The frontend depends on these exact strings.
    assert Regulator.NAFDAC.value == "NAFDAC"
    assert Severity.BLOCKING.value == "blocking"
    assert OverallStatus.NEEDS_ATTENTION.value == "needs_attention"


def test_invoice_round_trips_through_json() -> None:
    invoice = InvoiceExtraction(
        seller="Acme Chemicals Ltd",
        buyer="Lagos Importers Co",
        invoice_date=date(2026, 6, 1),
        currency="USD",
        incoterm="CIF",
        line_items=[LineItem(**_line_item())],
    )
    restored = InvoiceExtraction.model_validate_json(invoice.model_dump_json())
    assert restored == invoice
