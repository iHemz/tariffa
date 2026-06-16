"""Phase 0 agent round-trip endpoint.

Exposes the trivial Pydantic AI agent so the Next.js page can prove the full stack — browser →
FastAPI → Pydantic AI → Claude → typed result → browser — works end to end. Requires
ANTHROPIC_API_KEY; without it the agent call fails and this returns 503.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.agents.ping import Ping, run_ping

router = APIRouter(tags=["ping"])


@router.get("/ping", response_model=Ping)
async def ping() -> Ping:
    try:
        return await run_ping()
    except Exception as exc:  # surface a clean error instead of a 500 stack trace
        raise HTTPException(
            status_code=503,
            detail=f"Agent call failed (is ANTHROPIC_API_KEY set?): {exc}",
        ) from exc
