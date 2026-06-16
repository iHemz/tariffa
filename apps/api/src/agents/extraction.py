"""Extraction agent.

Reads uploaded invoices and packing lists and produces structured, typed data for downstream
stages. See docs/03-agent-pipeline.md for the responsibility, inputs/outputs, and known edge cases,
and docs/04-data-models.md for the Pydantic contract this agent must emit.

Stub only — define the Agent with its output_type (a Pydantic model from src/models) here.
"""

from __future__ import annotations
