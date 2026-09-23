# Common post schema

Every collector (news, Reddit, YouTube) must output records in this shape
before anything downstream (embeddings, clustering, scoring) touches them.
Do this normalization in `ingestion/`, not later — scoring and modeling
should never need to know which source a post came from.

```json
{
  "id": "string, source-prefixed, e.g. reddit_abc123",
  "source_type": "news | reddit | youtube",
  "source_name": "string, e.g. r/india, दैनिक भास्कर, channel handle",
  "text": "string, raw extracted text (Devanagari)",
  "url": "string",
  "timestamp": "ISO 8601 UTC",
  "author_id": "string",
  "author_followers": "int, null if unknown",
  "engagement": {
    "likes": "int",
    "shares": "int",
    "comments": "int"
  },
  "collected_at": "ISO 8601 UTC, when our pipeline ingested it"
}
```

## Notes

- `author_followers` is required for the influence score (Phase 3). If a
  source type can't expose it cheaply (e.g. some YouTube comment authors),
  default to `null` and the influence module should have a documented
  fallback (e.g. treat as median of known values), not silently drop the
  post.
- `engagement` numbers should be **raw counts at collection time**, not
  deltas. Velocity is computed downstream by comparing counts across
  repeated collection passes on the same post — so the collector needs to
  re-poll posts it has already seen, not just do a one-shot pull.
- Keep `text` as collected (no premature cleaning/stemming) — normalization
  for embeddings happens in `modeling/`, not `ingestion/`.
- OCR text (image posts) and transcript text (video posts) slot into the
  same `text` field once those modules exist — add a `content_format` field
  (`text | image_ocr | video_transcript`) when that day comes so scoring can
  weight OCR/transcript confidence differently if needed.
