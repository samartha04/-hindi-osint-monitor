"""
News RSS collector for the Hindi OSINT monitor.

Pulls entries from a list of Hindi-language news RSS feeds and normalizes
them into the common schema defined in docs/schema.md.

Usage:
    python ingestion/news_rss.py

Reads feed URLs from the NEWS_RSS_FEEDS env var (comma-separated), or from
ingestion/feeds.txt (one URL per line, # for comments) if that file exists.
Appends results to data/raw/news_<date>.jsonl.

This is meant to be run on a schedule (cron / GitHub Actions / a simple
`while true; do ...; sleep 900; done` loop during development) so that the
same articles get re-polled and engagement/comment counts can be diffed for
velocity later. It is intentionally simple — get it running and collecting
real data before making it clever.
"""

import os
import json
import hashlib
import datetime as dt
from pathlib import Path

import feedparser
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
FEEDS_FILE = REPO_ROOT / "ingestion" / "feeds.txt"
RAW_DIR = REPO_ROOT / "data" / "raw"


def load_feed_urls() -> list[str]:
    """Feed list priority: feeds.txt file, then env var, then a small
    built-in default set so the script runs out of the box for a demo."""
    if FEEDS_FILE.exists():
        urls = []
        for line in FEEDS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
        if urls:
            return urls

    env_urls = os.getenv("NEWS_RSS_FEEDS", "")
    if env_urls.strip():
        return [u.strip() for u in env_urls.split(",") if u.strip()]

    # Fallback defaults so `python ingestion/news_rss.py` works immediately.
    # Replace/extend these in ingestion/feeds.txt — verify each feed URL
    # still resolves before relying on it, outlets change RSS paths often.
    return [
        "https://www.bbc.com/hindi/index.xml",
    ]


def make_id(url: str) -> str:
    return "news_" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def parse_timestamp(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return dt.datetime(*t[:6], tzinfo=dt.timezone.utc).isoformat()
    return dt.datetime.now(dt.timezone.utc).isoformat()


def normalize_entry(entry, source_name: str) -> dict:
    text = entry.get("title", "")
    summary = entry.get("summary", "")
    if summary:
        text = f"{text}\n{summary}"

    return {
        "id": make_id(entry.get("link", entry.get("id", text))),
        "source_type": "news",
        "source_name": source_name,
        "text": text.strip(),
        "url": entry.get("link", ""),
        "timestamp": parse_timestamp(entry),
        "author_id": entry.get("author", source_name),
        "author_followers": None,  # not applicable for most news RSS
        "engagement": {"likes": 0, "shares": 0, "comments": 0},
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def collect(feed_urls: list[str]) -> list[dict]:
    records = []
    for url in feed_urls:
        parsed = feedparser.parse(url)
        if parsed.bozo:
            print(f"[warn] could not parse feed cleanly: {url} ({parsed.bozo_exception})")
        source_name = parsed.feed.get("title", url)
        for entry in parsed.entries:
            records.append(normalize_entry(entry, source_name))
        print(f"[ok] {source_name}: {len(parsed.entries)} entries")
    return records


def save(records: list[dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"news_{dt.date.today().isoformat()}.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out_path


def main():
    feed_urls = load_feed_urls()
    print(f"Collecting from {len(feed_urls)} feed(s)...")
    records = collect(feed_urls)
    out_path = save(records)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
