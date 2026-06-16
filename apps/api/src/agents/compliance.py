"""Compliance agent.

Flags compliance issues against real regulatory rules before they cause port delays. This agent MUST
be grounded in retrieved regulatory text (RAG via src/kb) — never the model's own unverified
knowledge of Nigerian customs law. See docs/03-agent-pipeline.md and
docs/06-regulatory-knowledge-base.md.

Stub only — define the Agent, its output_type, and the retrieval tool here.
"""

from __future__ import annotations
