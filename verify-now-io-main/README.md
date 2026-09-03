# VerifyNow — Fake Content Detection

A content-verification app that checks text, chat messages, website URLs,
documents, images, and video URLs against **real, retrieved evidence** — not
a heuristic, not a hash-based demo, not a hardcoded response table.

Every verdict (`VERIFIED` / `FALSE` / `MISLEADING` / `UNCERTAIN`) is produced
by a backend pipeline that does real web search via OpenAI's `web_search`
tool, fetches real page content, extracts real document/image text, and
returns `UNCERTAIN` whenever the evidence isn't there — it never invents a
confidence score, a source, a founder, or a date.

## Architecture

```
React (Vite) --> FastAPI --> Redis (cache + rate limit)
                     |
                     v
               PostgreSQL (results + evidence)
                     |
                     v
            Kafka (async verification jobs)
                     |
                     v
        Worker --> OpenAI (web-search-grounded
                    reasoning) + document/image
                    extraction + optional HF model
```

- **Frontend**: React + Vite + TypeScript + shadcn/ui (unchanged design,
  rewired to call the real backend).
- **Backend**: FastAPI, async SQLAlchemy (Postgres), Redis, Kafka.
- **Verification**: a two-pass OpenAI Responses API flow — pass 1 researches
  the claim with the `web_search` tool, pass 2 forces a strict structured
  JSON result using only what pass 1 actually found.
- **Infra**: Docker Compose wiring every service above.

See [`backend/README.md`](backend/README.md) for backend-specific details.

## Quick start (Docker Compose — recommended)

```sh
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

docker compose up --build
```

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000 (docs at `/docs`)
- Postgres: localhost:5432, Redis: localhost:6379, Kafka: localhost:9092

Without `OPENAI_API_KEY` set, the app still runs end-to-end, but every
verification returns `UNCERTAIN` with an explicit "no API key configured"
limitation — this is intentional; it never falls back to fake data.

## Running locally without Docker

**Backend**

```sh
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY, and point DATABASE_URL/REDIS_URL
                        # at local instances, or set KAFKA_ENABLED=false to
                        # skip needing a Kafka broker for local dev

uvicorn app.main:app --reload --port 8000
```

If `KAFKA_ENABLED=false`, the API processes verification requests in-process
via an asyncio background task instead of publishing to Kafka — same
verification logic, different dispatch, purely for environments without a
broker running. The default and production path (Docker Compose) always uses
Kafka with a real consumer worker (`python -m app.worker.consumer`).

**Frontend**

```sh
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

## Tests

```sh
cd backend
pip install -r requirements.txt
pytest -q
```

18 tests cover: the submit -> poll API flow, VERIFIED/UNCERTAIN outcomes,
URL-fetch failure handling, document parsing, 404s, history, and the
two-pass OpenAI verification logic — all with external calls mocked so they
run without live credentials or network access.

Frontend has no automated tests yet (see Known Limitations). Verify the
build with:

```sh
npm run build
```

## What's real vs. what's a documented gap

**Real and working:**
- Text/chat, website URL, document (PDF/DOCX/TXT), and image verification,
  all backed by the same web-search-grounded pipeline
- Website intelligence that separates "the site claims X" from
  "an independent source verifies X"
- Redis caching + rate limiting, Postgres persistence of results/evidence,
  Kafka-dispatched async processing with a real consumer worker
- Honest `UNCERTAIN` fallback on any failure (missing API key, fetch error,
  unparseable model output, insufficient evidence)

**Documented gaps** (see `backend/README.md` -> Known Limitations for detail):
- Video is metadata-only (URL page title/description), not actual video/audio
  analysis — there was never a real way to do full video content analysis
  within this project's scope, so the UI is explicit about that instead of
  faking it.
- The optional AI-generated-text signal (HuggingFace) is off by default and
  never influences the verdict, per spec.
- No CLIP-based image-manipulation detection — image handling here extracts
  the claim shown in the image and verifies *that*, rather than assessing
  pixel-level tampering.
- No Alembic migrations yet (tables are created via `create_all` on startup),
  no frontend test suite, no CI pipeline.
- `docker compose config`/`build` could not be executed in the environment
  this was built in (no Docker engine available there); the compose file was
  validated structurally instead (YAML parse + confirmed every referenced
  Dockerfile path resolves). Run `docker compose config` yourself before
  deploying to confirm it builds in your environment.
