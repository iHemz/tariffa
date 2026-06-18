# Project Constraints

- I am using git bash as a terminal, so unix commands work
- pnpm is the package manager for the frontend (`apps/web`); uv manages the Python backend (`apps/api`)
- Frontend checks: `pnpm --filter web run typecheck` for types, `pnpm --filter web run lint` for linting
- Backend checks: `ruff check apps/api` for linting, `ruff format apps/api` for formatting, `pytest` (run from `apps/api`) for tests
