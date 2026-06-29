# Tariffa API container image. Build context is apps/api (this directory), so the monorepo's
# backend is self-contained. Used by Fly.io (see fly.toml) and works on any container host.

FROM python:3.13-slim

# uv: fast, reproducible installs from uv.lock (https://docs.astral.sh/uv/guides/integration/docker/)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Compile to bytecode for faster cold starts; copy (not hardlink) into the image layer.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies first, against the lockfile only, so this layer is cached unless deps change.
# --no-dev drops pytest/ruff/reportlab (not needed at runtime).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application and finish the sync.
COPY . .
RUN uv sync --frozen --no-dev

# Fly routes to this port (fly.toml internal_port). Bind to 0.0.0.0 so it's reachable.
EXPOSE 8080
CMD ["uv", "run", "--no-dev", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
