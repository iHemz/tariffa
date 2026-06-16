"""FastAPI application entrypoint.

Owns agent orchestration, the database, file storage, and all LLM calls. The web app is a thin
client and never talks to Postgres, S3, or the Claude API directly.

Run locally:
    uv run uvicorn src.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import health

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open the database pool here (see src/db.py) once a DATABASE_URL is configured.
    yield
    # Shutdown: close the pool here.


app = FastAPI(title="Tariffa API", version="0.1.0", lifespan=lifespan)

# The frontend (http://localhost:3000) is the only browser origin in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
