"""
Unit tests for ingestion/youtube_collector.py normalization logic.
Uses fake API response dicts instead of hitting the YouTube Data API.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.youtube_collector import normalize_video, normalize_comment, get_transcript


def test_normalize_video_basic_fields():
    fake_item = {
        "id": {"videoId": "xyz789"},
        "snippet": {
            "title": "वायरल खबर: बड़ा दावा",
            "description": "पूरी जानकारी विवरण में",
            "channelTitle": "News Channel",
            "channelId": "UC12345",
            "publishedAt": "2026-09-20T10:00:00Z",
        },
    }
    record = normalize_video(fake_item, subscriber_count=500000)

    assert record["id"] == "youtube_xyz789"
    assert record["source_type"] == "youtube"
    assert "वायरल खबर" in record["text"]
    assert record["url"] == "https://www.youtube.com/watch?v=xyz789"
    assert record["author_followers"] == 500000
    assert record["timestamp"] == "2026-09-20T10:00:00Z"


def test_normalize_comment_basic_fields():
    video_record = {"source_name": "News Channel", "url": "https://www.youtube.com/watch?v=xyz789"}
    fake_comment = {
        "id": "comment1",
        "snippet": {
            "topLevelComment": {
                "snippet": {
                    "textDisplay": "यह सच नहीं लगता",
                    "authorDisplayName": "user123",
                    "publishedAt": "2026-09-20T11:00:00Z",
                    "likeCount": 12,
                }
            },
            "totalReplyCount": 3,
        },
    }
    record = normalize_comment(fake_comment, video_record)

    assert record["id"] == "youtube_comment_comment1"
    assert "यह सच नहीं लगता" in record["text"]
    assert record["author_followers"] is None
    assert record["engagement"]["likes"] == 12
    assert record["engagement"]["comments"] == 3


def test_transcript_stub_returns_none():
    # Explicit stub — this test documents the contract so nobody forgets
    # to update it once transcript extraction is actually implemented.
    assert get_transcript("any_video_id") is None
