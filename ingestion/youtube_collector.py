"""
YouTube collector for the Hindi OSINT monitor.

Pulls recent videos matching Hindi-language search queries (and/or from a
fixed channel list) plus their top comments, normalized into the common
schema in docs/schema.md.

Setup:
    1. Enable "YouTube Data API v3" in Google Cloud Console, create an API key
    2. Fill YOUTUBE_API_KEY in .env

Usage:
    python ingestion/youtube_collector.py

Reads search queries from ingestion/youtube_queries.txt. Appends results to
data/raw/youtube_<date>.jsonl.

Scope note: this collects video titles/descriptions/top comments only (text-
native). Transcript extraction (spoken content) is explicitly out of MVP
scope per docs/scope discussion — see the transcript stub function at the
bottom, left unimplemented on purpose so the interface exists without
blocking Phase 1-3 on solving Hindi ASR/caption reliability.
"""

import os
import json
import datetime as dt
from pathlib import Path

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_FILE = REPO_ROOT / "ingestion" / "youtube_queries.txt"
RAW_DIR = REPO_ROOT / "data" / "raw"

VIDEOS_PER_QUERY = 15
COMMENTS_PER_VIDEO = 20


def get_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY missing. Copy .env.example to .env and fill it "
            "in — create one at https://console.cloud.google.com/apis/credentials "
            "after enabling 'YouTube Data API v3'."
        )
    return build("youtube", "v3", developerKey=api_key)


def load_queries() -> list[str]:
    if QUERIES_FILE.exists():
        queries = []
        for line in QUERIES_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                queries.append(line)
        if queries:
            return queries
    return ["समाचार आज"]  # "news today" — fallback so this runs out of the box


def search_videos(youtube, query: str) -> list[dict]:
    response = (
        youtube.search()
        .list(
            q=query,
            part="snippet",
            type="video",
            relevanceLanguage="hi",
            order="date",
            maxResults=VIDEOS_PER_QUERY,
        )
        .execute()
    )
    return response.get("items", [])


def get_channel_stats(youtube, channel_ids: list[str]) -> dict:
    """Batch-fetch subscriber counts (our influence/reach proxy for YouTube)."""
    if not channel_ids:
        return {}
    stats = {}
    # API allows up to 50 ids per call
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        response = (
            youtube.channels().list(part="statistics", id=",".join(batch)).execute()
        )
        for item in response.get("items", []):
            sub_count = item["statistics"].get("subscriberCount")
            stats[item["id"]] = int(sub_count) if sub_count is not None else None
    return stats


def normalize_video(item: dict, subscriber_count) -> dict:
    snippet = item["snippet"]
    video_id = item["id"]["videoId"]
    text = f"{snippet.get('title', '')}\n{snippet.get('description', '')}"

    return {
        "id": f"youtube_{video_id}",
        "source_type": "youtube",
        "source_name": snippet.get("channelTitle", ""),
        "text": text.strip(),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "timestamp": snippet.get("publishedAt", dt.datetime.now(dt.timezone.utc).isoformat()),
        "author_id": snippet.get("channelId", ""),
        "author_followers": subscriber_count,
        "engagement": {"likes": 0, "shares": 0, "comments": 0},  # filled in after stats call
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def normalize_comment(comment_item: dict, video_record: dict) -> dict:
    snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
    return {
        "id": f"youtube_comment_{comment_item['id']}",
        "source_type": "youtube",
        "source_name": f"comment on {video_record['source_name']}",
        "text": snippet.get("textDisplay", ""),
        "url": video_record["url"],
        "timestamp": snippet.get("publishedAt", dt.datetime.now(dt.timezone.utc).isoformat()),
        "author_id": snippet.get("authorDisplayName", ""),
        "author_followers": None,  # comment authors' reach isn't meaningful here
        "engagement": {
            "likes": snippet.get("likeCount", 0),
            "shares": 0,
            "comments": comment_item["snippet"].get("totalReplyCount", 0),
        },
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def get_comments(youtube, video_id: str) -> list[dict]:
    try:
        response = (
            youtube.commentThreads()
            .list(part="snippet", videoId=video_id, maxResults=COMMENTS_PER_VIDEO, order="relevance")
            .execute()
        )
        return response.get("items", [])
    except Exception as e:
        # Comments can be disabled on a video — that's normal, not an error
        # worth crashing the whole collection run over.
        print(f"[warn] could not fetch comments for {video_id}: {e}")
        return []


def get_transcript(video_id: str) -> str | None:
    """
    STUB — out of MVP scope. Hindi auto-captions are unreliable and often
    code-switch with English mid-sentence; solving this properly is a
    project in itself. Left as an explicit interface so modeling/ can be
    written against a `content_format: video_transcript` field once this
    is implemented, without a later refactor. Returns None until then.
    """
    return None


def collect(youtube, queries: list[str]) -> list[dict]:
    records = []
    channel_ids = set()
    video_items = []

    for query in queries:
        items = search_videos(youtube, query)
        video_items.extend(items)
        for item in items:
            channel_ids.add(item["snippet"]["channelId"])
        print(f"[ok] query '{query}': {len(items)} videos")

    channel_stats = get_channel_stats(youtube, list(channel_ids))

    for item in video_items:
        channel_id = item["snippet"]["channelId"]
        video_record = normalize_video(item, channel_stats.get(channel_id))
        records.append(video_record)

        video_id = item["id"]["videoId"]
        for comment_item in get_comments(youtube, video_id):
            records.append(normalize_comment(comment_item, video_record))

    return records


def save(records: list[dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"youtube_{dt.date.today().isoformat()}.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out_path


def main():
    youtube = get_client()
    queries = load_queries()
    print(f"Collecting from {len(queries)} search quer{'y' if len(queries)==1 else 'ies'}...")
    records = collect(youtube, queries)
    out_path = save(records)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
