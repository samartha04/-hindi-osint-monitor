"""
Unit tests for ingestion/news_rss.py normalization logic.
No network calls — feedparser entries are faked as plain dicts.
Run with: pytest tests/test_news_rss.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.news_rss import make_id, normalize_entry


def test_make_id_is_stable():
    url = "https://example.com/article-1"
    assert make_id(url) == make_id(url)


def test_make_id_differs_for_different_urls():
    assert make_id("https://example.com/a") != make_id("https://example.com/b")


def test_normalize_entry_basic_fields():
    fake_entry = {
        "title": "बाढ़ से भारी नुकसान",
        "summary": "राहत कार्य जारी",
        "link": "https://example.com/flood-news",
        "author": "संवाददाता",
        "published_parsed": (2026, 9, 20, 10, 30, 0, 0, 0, 0),
    }
    record = normalize_entry(fake_entry, source_name="Test News")

    assert record["source_type"] == "news"
    assert record["source_name"] == "Test News"
    assert "बाढ़" in record["text"]
    assert "राहत कार्य जारी" in record["text"]
    assert record["url"] == "https://example.com/flood-news"
    assert record["author_followers"] is None
    assert record["engagement"] == {"likes": 0, "shares": 0, "comments": 0}
    assert record["timestamp"].startswith("2026-09-20")


def test_normalize_entry_missing_fields_does_not_crash():
    fake_entry = {"title": "शीर्षक केवल"}
    record = normalize_entry(fake_entry, source_name="Test News")
    assert record["text"] == "शीर्षक केवल"
    assert record["url"] == ""
    assert record["author_id"] == "Test News"
