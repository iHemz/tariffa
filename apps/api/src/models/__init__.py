"""Pydantic schemas — the typed contracts between pipeline stages.

Every agent-to-agent handoff is a validated Pydantic model; no raw dicts cross a pipeline boundary.
One module per stage (extraction -> classification -> compliance -> form); shared enums live in
`common`. Import from here for the stable public surface.

See docs/04-data-models.md for the rationale behind each field.
"""

from src.models.classification import ClassificationResult
from src.models.common import OverallStatus, Regulator, Severity
from src.models.compliance import ComplianceFlag, ComplianceReport
from src.models.extraction import InvoiceExtraction, LineItem
from src.models.form import FormDraft

__all__ = [
    "ClassificationResult",
    "ComplianceFlag",
    "ComplianceReport",
    "FormDraft",
    "InvoiceExtraction",
    "LineItem",
    "OverallStatus",
    "Regulator",
    "Severity",
]
