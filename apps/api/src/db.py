"""Database access.

Single Postgres instance holds both relational data and the knowledge-base embeddings (pgvector) —
no separate vector store at this scale. Enable the extension once per database:

    CREATE EXTENSION IF NOT EXISTS vector;

This module is a placeholder until Phase 0 needs the database. Wire the pool into the FastAPI
lifespan in src/main.py when you do.
"""

from __future__ import annotations

import os

import asyncpg

_pool: asyncpg.Pool | None = None


async def connect() -> asyncpg.Pool:
    """Open the shared connection pool (call once on startup)."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=os.environ["DATABASE_URL"])
    return _pool


async def disconnect() -> None:
    """Close the shared connection pool (call once on shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
