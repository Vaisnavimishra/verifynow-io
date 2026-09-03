# VerifyNow Backend

FastAPI service that performs real, evidence-based content verification.

## Environment variables

See `.env.example`. The most important one is `OPENAI_API_KEY` — without it,
`app/services/openai_verification.py` returns `UNCERTAIN` with an explicit
limitation message rather than attempting any verification.

## API

- `POST /api/verify` (multipart form) — submit content for verification.
  - `content_type`: `text` | `url` | `document` | `image` | `video_url`
  - `text`: required for `text`/`url`/`video_url`
  - `file`: required for `document`/`image`
  - Returns `202` with `{request_id, status}`.
- `GET /api/verify/{request_id}` — poll for the result. `status` is one of
  `pending` / `processing` / `completed` / `failed`.
- `GET /api/history?limit=20` — recent submissions.
- `GET /health` — liveness check.

## Processing pipeline (`app/services/pipeline.py`)

1. Cache check (Redis) for `text`/`url` submissions, keyed by a hash of the
   normalized content.
2. Build the real "subject + context" for the LLM:
   - `text`: the text itself.
   - `url`: server-side fetch of the actual page (`app/services/web_fetch.py`)
     — title, meta description, site name, published time, body excerpt.
   - `document`: text extracted server-side from the uploaded PDF/DOCX/TXT
     (`app/services/document_parser.py`).
   - `image`: the claim/caption extracted via OpenAI vision
     (`app/services/image_analysis.py`).
   - `video_url`: page metadata only (see Known Limitations).
3. Two-pass OpenAI verification (`app/services/openai_verification.py`):
   research with `web_search`, then force strict structured JSON from that
   research. Any failure (no key, API error, bad JSON) yields `UNCERTAIN`
   with a specific `limitations` string — never fabricated content.
4. Persist the result (`AnalysisRequest` + `EvidenceSource` rows) and cache it
   for cacheable content types.

Dispatch: Kafka producer/consumer by default
(`app/services/kafka_bus.py` + `app/worker/consumer.py`); an in-process
asyncio fallback when `KAFKA_ENABLED=false`, useful for local dev without a
broker. Both paths call the exact same `process_verification_request`.

## Known limitations

- **Video**: only URL submissions are accepted, and only page metadata
  (title/description) is fetched — there is no audio transcription or
  frame-level video analysis in this MVP. This is reflected in the UI copy,
  not hidden.
- **Image analysis** extracts and verifies the *claim* shown in an image via
  OpenAI vision. It does not do CLIP-based or forensic manipulation/deepfake
  detection — that was descoped for this MVP; `app/services/ai_text_detector.py`
  shows the intended extension point pattern if you want to add a real model
  later (same "never affects the factual verdict" constraint should apply to
  any image-authenticity signal added the same way).
- **AI-generated-text detection** (`app/services/ai_text_detector.py`) is
  disabled unless `AI_TEXT_DETECTOR_MODEL` is set to a HuggingFace
  text-classification model id, and `transformers`/`torch` are installed
  (commented out in `requirements.txt` by default since they're heavy). When
  enabled, it is surfaced as a separate signal and never used to justify a
  verdict, per spec.
- **Migrations**: tables are created via `Base.metadata.create_all` on
  startup, not Alembic. Fine for an MVP; add Alembic before any schema
  changes need to ship without data loss in production.
- **Rate limiting** is a simple fixed-window counter per client IP in Redis;
  fine for an MVP, not suitable as your only defense against abuse in
  production (consider a sliding window + auth-based limits).
- **Caching** is content-hash based per `(content_type, normalized_value)`;
  a URL's cached verdict can go stale if the underlying page changes before
  `CACHE_TTL_SECONDS` elapses.
