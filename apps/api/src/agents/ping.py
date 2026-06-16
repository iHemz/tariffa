"""Phase 0 trivial agent.

The smallest possible Pydantic AI agent: it calls Claude and returns a typed result, nothing more.
Its only purpose is to prove the full stack talks to itself end to end (see docs/05-build-phases.md,
Phase 0) before any real pipeline logic exists. The four real pipeline agents live alongside this as
stubs.

Requires ANTHROPIC_API_KEY in the environment (pydantic-ai bundles the Anthropic provider).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel
from pydantic_ai import Agent


class Ping(BaseModel):
    """Typed output contract for the ping agent."""

    message: str
    """A short, friendly confirmation that the model round-trip worked."""


@lru_cache(maxsize=1)
def get_ping_agent() -> Agent[None, Ping]:
    """Build the agent lazily.

    Constructing the Agent eagerly initializes the Anthropic provider, which requires
    ANTHROPIC_API_KEY just to import. Deferring it keeps the app (and /health) importable without a
    key — only /ping needs one. Default to the latest Claude model; if cost ever matters for this
    one-off health check, switch to "anthropic:claude-haiku-4-5" — the typed contract is unchanged.
    """
    return Agent(
        "anthropic:claude-opus-4-8",
        output_type=Ping,
        system_prompt=(
            "You are a health-check agent for Tariffa, a tool that helps Nigerian freight "
            "forwarders pre-check import documentation. Reply with one short, friendly sentence "
            "confirming the pipeline is reachable."
        ),
    )


async def run_ping() -> Ping:
    """Run the agent once and return its typed output."""
    result = await get_ping_agent().run("Say hello and confirm the agent pipeline is wired up.")
    return result.output
