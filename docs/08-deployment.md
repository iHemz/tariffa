# Deployment

Two services, two hosts (see `02-architecture.md`):

| Service | Host | Why |
|---|---|---|
| `apps/api` (FastAPI) | **Fly.io** | Runs Python + managed Postgres w/ pgvector, push-to-deploy |
| `apps/web` (Next.js) | **Vercel** | Zero-config Next.js, free tier covers a side project |

## Order of operations (this order matters)

The frontend needs the backend's URL, and the backend's CORS needs the frontend's URL — so:

1. **Deploy the backend** to Fly → get `https://<app>.fly.dev`.
2. **Deploy the frontend** to Vercel with `NEXT_PUBLIC_API_URL = https://<app>.fly.dev` → get `https://<app>.vercel.app`.
3. **Point the backend's CORS at the frontend**: `fly secrets set ALLOWED_ORIGINS=https://<app>.vercel.app` (this redeploys). Now the browser calls succeed end to end.

Until step 3, the deployed frontend loads but its API calls are blocked by CORS — that's expected, not a bug.

---

## Backend → Fly.io

Config already in the repo: `apps/api/Dockerfile`, `apps/api/.dockerignore`, `apps/api/fly.toml`
(region `jnb`/Johannesburg, scales to zero when idle, health-checks `/health`).

### 1. Install flyctl + sign in

Windows (PowerShell):
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```
Then `fly auth signup` (new) or `fly auth login`. (Fly requires a card even on the free allowance.)

### 2. Create the app

From `apps/api`:
```bash
fly launch --no-deploy
```
When it finds the existing `fly.toml`, **accept it / "copy configuration"**, pick a **globally-unique app name** and region **jnb**. It updates `app = "..."` in `fly.toml` to your chosen name — commit that change.

### 3. Set secrets

```bash
# from apps/api (or add -a <your-app-name>)
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
```
`ALLOWED_ORIGINS` is set in step 3 of the order above, once you know the Vercel domain.

### 4. Deploy + verify

```bash
fly deploy            # builds the Dockerfile, deploys
fly open /health      # → {"status":"ok","service":"tariffa-api"}
```
`/ping` exercises the full Claude round-trip (needs `ANTHROPIC_API_KEY`). Your public URL is
`https://<app>.fly.dev`. Logs: `fly logs`.

### Postgres + pgvector — later, not needed for the first deploy

The app boots and `/health` + `/ping` work without a database (the DB lifespan is still a
placeholder — see `TODO.md`). When persistence lands:
```bash
fly postgres create                       # or Fly Managed Postgres
fly postgres attach <pg-app> -a <api-app> # sets the DATABASE_URL secret automatically
fly postgres connect -a <pg-app>          # then run:  CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Frontend → Vercel

1. vercel.com → **Add New → Project** → import `iHemz/tariffa`.
2. **Root Directory = `apps/web`** (the one critical monorepo setting).
3. Framework **Next.js** auto-detected; leave Build/Output/Install on their defaults.
4. **Environment Variables** → add `NEXT_PUBLIC_API_URL = https://<app>.fly.dev` (your Fly URL).
5. **Deploy.** Then do step 3 of "Order of operations" so the backend allows the Vercel origin.

CLI alternative from `apps/web`: `npx vercel` then `npx vercel --prod`.

---

## Environment variables reference

**Backend (`apps/api`) — Fly secrets (`fly secrets set ...`):**

| Var | Needed for | When |
|---|---|---|
| `ANTHROPIC_API_KEY` | `/ping`, all agents | now |
| `ALLOWED_ORIGINS` | browser CORS from the Vercel domain (comma-separated) | after frontend is deployed |
| `DATABASE_URL` | persistence + RAG | when DB lands (set by `fly postgres attach`) |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET` | presigned uploads | when uploads land |

**Frontend (`apps/web`) — Vercel env:**

| Var | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<app>.fly.dev` |

The frontend only ever holds the API URL — never the Anthropic key, DB URL, or AWS creds.

---

## Troubleshooting

- **Frontend loads, API badges fail** → backend not deployed, `NEXT_PUBLIC_API_URL` wrong, or
  `ALLOWED_ORIGINS` doesn't include the exact Vercel origin (scheme + host, no trailing slash).
- **`/ping` returns 503** → `ANTHROPIC_API_KEY` not set on Fly (`fly secrets list` to check).
- **Machine OOM / restarts** → bump `memory` in `fly.toml` from `1gb` (e.g. to `2gb`) and redeploy.
- **Cold-start latency** → expected with scale-to-zero; set `min_machines_running = 1` in `fly.toml`
  to keep one warm (costs more).
