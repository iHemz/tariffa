"""Shared enums used across more than one pipeline stage.

Kept separate so the per-stage contract modules (extraction, classification, compliance, form) can
import a single source of truth rather than redefining string literals.
"""

from __future__ import annotations

from enum import Enum


class Regulator(str, Enum):
    """Nigerian regulators a line item can fall under."""

    NAFDAC = "NAFDAC"
    SON = "SON"
    NONE = "NONE"


class Severity(str, Enum):
    """How serious a compliance flag is for the shipment."""

    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class OverallStatus(str, Enum):
    """Roll-up verdict for a compliance report."""

    CLEAR = "clear"
    NEEDS_ATTENTION = "needs_attention"
    BLOCKED = "blocked"
