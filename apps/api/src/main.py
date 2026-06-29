"""FastAPI application entrypoint.

Owns agent orchestration, the database, file storage, and all LLM calls. The web app is a thin
client and never talks to Postgres, S3, or the Claude API directly.

Run locally:
    uv run uvicorn src.main:app --reload
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import health, ping

load_dotenv()

# Browser origins allowed to call this API. Defaults to the local dev frontend; in production set
# ALLOWED_ORIGINS to the deployed web origin(s), comma-separated — e.g.
# "https://tariffa.vercel.app,https://tariffa-git-main.vercel.app".
_DEFAULT_ORIGINS = "http://localhost:3000"
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open the database pool here (see src/db.py) once a DATABASE_URL is configured.
    yield
    # Shutdown: close the pool here.


app = FastAPI(title="Tariffa API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ping.router)
