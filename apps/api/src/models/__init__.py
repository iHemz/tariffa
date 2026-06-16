"""Pydantic schemas — the typed contracts between pipeline stages.

Every agent-to-agent handoff is a validated Pydantic model; no raw dicts cross a pipeline boundary.
Define the concrete models here per docs/04-data-models.md.
"""
