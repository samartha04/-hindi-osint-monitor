"""
Unit tests for ingestion/reddit_collector.py normalization logic.
Uses a minimal fake submission object instead of hitting Reddit's API.
"""

import sys
import datetime as dt
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.reddit_collector import normalize_submission


def make_fake_submission(**overrides):
    defaults = dict(
        id="abc123",
        title="बाढ़ राहत निधि में घोटाले का दावा",
        selftext="",
        author=SimpleNamespace(__str__=lambda self: "some_user"),
        permalink="/r/india/comments/abc123/flood_claim/",
        created_utc=dt.datetime(2026, 9, 20, tzinfo=dt.timezone.utc).timestamp(),
        score=245,
        num_comments=38,
        subreddit=SimpleNamespace(display_name="india"),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_normalize_submission_basic_fields():
    submission = make_fake_submission()
    record = normalize_submission(submission)

    assert record["id"] == "reddit_abc123"
    assert record["source_type"] == "reddit"
    assert record["source_name"] == "r/india"
    assert "घोटाले" in record["text"]
    assert record["url"].endswith("/r/india/comments/abc123/flood_claim/")
    assert record["engagement"]["likes"] == 245
    assert record["engagement"]["comments"] == 38
    assert record["timestamp"].startswith("2026-09-20")


def test_normalize_submission_includes_selftext():
    submission = make_fake_submission(selftext="अतिरिक्त विवरण यहाँ है")
    record = normalize_submission(submission)
    assert "अतिरिक्त विवरण यहाँ है" in record["text"]


def test_normalize_submission_deleted_author():
    submission = make_fake_submission(author=None)
    record = normalize_submission(submission)
    assert record["author_id"] == "[deleted]"
