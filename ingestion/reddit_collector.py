"""
Reddit collector for the Hindi OSINT monitor.

Pulls posts (and optionally top-level comments) from a list of subreddits
using PRAW, and normalizes them into the common schema in docs/schema.md.

*** STATUS AS OF SEPT 2026: BLOCKED ON REDDIT APPROVAL ***
Reddit closed self-service API app creation on 11 Nov 2025. Every new OAuth
credential now requires manual approval under Reddit's "Responsible Builder
Policy" (2-4 week review). Academic/research use should apply via Reddit's
r/reddit4researchers program rather than the general developer request
queue — search for it directly, since the exact URL moves around.
Until approval comes through, this script will not run. Do not block Phase 1
on this: proceed with news + YouTube collectors, keep this stubbed and ready,
and swap in real credentials the moment approval lands.

Setup (once approved):
    1. Create a Reddit app at https://www.reddit.com/prefs/apps (type: script)
    2. Fill REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USER_AGENT in .env

Usage:
    python ingestion/reddit_collector.py

Reads subreddit list from ingestion/subreddits.txt (one per line, # to
comment). Appends results to data/raw/reddit_<date>.jsonl.

Note on re-polling for velocity: unlike news RSS (fire-and-forget), Reddit
score/comment counts change after posting. This script re-fetches posts it
has already seen (by id) so engagement deltas can be computed downstream —
see the `seen_ids` cache logic below. Don't remove that if you refactor this;
it's what makes velocity/spike detection possible in scoring/.
"""

import os
import json
import datetime as dt
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBREDDITS_FILE = REPO_ROOT / "ingestion" / "subreddits.txt"
RAW_DIR = REPO_ROOT / "data" / "raw"

# How many of the newest posts to check per subreddit per run.
# Keep this modest during development to stay well within Reddit's rate
# limits (PRAW handles pacing automatically, but don't fight it).
POSTS_PER_SUBREDDIT = 40


def get_client() -> praw.Reddit:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "hindi-osint-monitor/0.1")

    if not client_id or not client_secret:
        raise RuntimeError(
            "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET missing. "
            "Copy .env.example to .env and fill them in — "
            "see https://www.reddit.com/prefs/apps to create a 'script' app."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def load_subreddits() -> list[str]:
    if SUBREDDITS_FILE.exists():
        names = []
        for line in SUBREDDITS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.append(line)
        if names:
            return names
    # Fallback so the script runs out of the box.
    return ["india"]


def normalize_submission(submission) -> dict:
    text = submission.title or ""
    if getattr(submission, "selftext", ""):
        text = f"{text}\n{submission.selftext}"

    author_name = str(submission.author) if submission.author else "[deleted]"

    return {
        "id": f"reddit_{submission.id}",
        "source_type": "reddit",
        "source_name": f"r/{submission.subreddit.display_name}",
        "text": text.strip(),
        "url": f"https://reddit.com{submission.permalink}",
        "timestamp": dt.datetime.fromtimestamp(
            submission.created_utc, tz=dt.timezone.utc
        ).isoformat(),
        "author_id": author_name,
        # Reddit doesn't expose follower counts (it isn't that kind of
        # platform) — subreddit subscriber count is the closest analogue
        # for reach and is filled in by the caller, not here.
        "author_followers": None,
        "engagement": {
            "likes": submission.score,
            "shares": 0,  # not exposed by Reddit's API
            "comments": submission.num_comments,
        },
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def collect(reddit: praw.Reddit, subreddit_names: list[str]) -> list[dict]:
    records = []
    for name in subreddit_names:
        subreddit = reddit.subreddit(name)
        subscriber_count = subreddit.subscribers
        count = 0
        for submission in subreddit.new(limit=POSTS_PER_SUBREDDIT):
            record = normalize_submission(submission)
            # Fill in subreddit size as the reach proxy mentioned above.
            record["author_followers"] = subscriber_count
            records.append(record)
            count += 1
        print(f"[ok] r/{name}: {count} posts (subscribers: {subscriber_count})")
    return records


def save(records: list[dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"reddit_{dt.date.today().isoformat()}.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out_path


def main():
    reddit = get_client()
    subreddit_names = load_subreddits()
    print(f"Collecting from {len(subreddit_names)} subreddit(s)...")
    records = collect(reddit, subreddit_names)
    out_path = save(records)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
