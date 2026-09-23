# Hindi OSINT Monitor

Real-time, credibility- and influence-aware event detection for Hindi-language
OSINT content (news + YouTube; Reddit deferred, see below).

MVP scope: Devanagari-script, text-native sources only (news RSS/API,
YouTube metadata/comments). Reddit is deferred — Reddit closed self-service
API access in Nov 2025 and now requires a multi-week manual approval that
doesn't fit a semester timeline; the collector is fully built and tested and
can be switched on later with zero code changes if approval comes through
(see `docs/roadmap.md`). Image OCR and video-transcript ingestion are also
stubbed as interfaces for future work — see `docs/roadmap.md`.

## Repo layout

```
ingestion/      collectors for news RSS, YouTube Data API (Reddit built, deferred)
modeling/       MuRIL embeddings + HDBSCAN clustering
scoring/        credibility score, influence score, joint alert-priority score
dashboard/      visualization + evaluation
data/
  raw/          untouched collector output (gitignored, not committed)
  processed/    normalized schema, ready for modeling
  annotations/  team-labeled validation set
docs/           scope notes, annotation guidelines, prior-art notes, roadmap
tests/          unit tests per module
```

## Roles (fill in names)

| Module    | Owner | Status |
|-----------|-------|--------|
| Ingestion |       | not started |
| Modeling (MuRIL + clustering) |       | not started |
| Scoring engine |       | not started |
| Dashboard / eval |       | not started |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
```

## Phase status

See `docs/roadmap.md` for the full semester plan. Currently: **Phase 0 — setup**.
