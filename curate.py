#!/usr/bin/env python3
"""
curate.py — Optional RSS pre-fetch for AI Signal curation.

Fetches recent RSS entries for existing sources AND any candidates listed in
candidates.yaml, writing everything to _curate_context.json.

This is supplementary data — web search (via /curate or /scan-sources) is the
primary and more reliable signal for source activity.

Usage:
    python -m pip install pyyaml feedparser
    python curate.py

Then run /curate or /scan-sources in Claude Code.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import feedparser
    import yaml
except ImportError:
    print("Missing deps. Run: python -m pip install pyyaml feedparser")
    sys.exit(1)

LOOKBACK_DAYS = 90
OUTPUT_FILE = Path("_curate_context.json")
SOURCES_FILE = Path("sources.yaml")
CANDIDATES_FILE = Path("candidates.yaml")


def load_sources(path: Path) -> list[dict]:
    with path.open() as f:
        return yaml.safe_load(f)["sources"]


def load_candidates(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        data = yaml.safe_load(f)
    return data.get("candidates") or []


def fetch_recent_entries(rss_url: str, since: datetime) -> list[dict]:
    """
    Fetch feed entries published since `since`. Returns [] on any failure —
    treat an empty result as 'RSS unreliable', not 'source inactive'. Always
    verify source activity via web search before drawing conclusions.
    """
    try:
        feed = feedparser.parse(rss_url)
        entries = []
        for entry in feed.entries[:20]:
            for field in ("published_parsed", "updated_parsed"):
                t = getattr(entry, field, None)
                if t:
                    dt = datetime(*t[:6], tzinfo=timezone.utc)
                    if dt >= since:
                        entries.append({
                            "title": getattr(entry, "title", ""),
                            "url": getattr(entry, "link", ""),
                            "date": dt.strftime("%Y-%m-%d"),
                            "summary": getattr(entry, "summary", "")[:300],
                        })
                    break
        return entries
    except Exception:
        return []


def process_source(s: dict, since: datetime, label: str) -> dict:
    rss = s.get("rss")
    recent = []
    if rss:
        recent = fetch_recent_entries(rss, since)
        status = f"{len(recent)} recent posts" if recent else "0 posts (RSS may be broken — verify via web search)"
    else:
        status = "no RSS"
    print(f"  [{label}] {s.get('name', s.get('url', '?'))} ... {status}")
    return {
        "name": s.get("name", ""),
        "url": s.get("url", ""),
        "rss": rss or "",
        "type": s.get("type", ""),
        "depth": s.get("depth", ""),
        "audience": s.get("audience", []),
        "tags": s.get("tags", []),
        "activity": s.get("activity", ""),
        "last_checked": s.get("last_checked", ""),
        "landmark_posts": s.get("landmark_posts", []),
        "recent_posts": recent,
        "rss_reliable": bool(recent),
    }


def main():
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    context = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": LOOKBACK_DAYS,
        "note": "0 recent_posts means RSS parsing failed or feed is genuinely quiet. Always verify via web search.",
        "sources": [],
        "candidates": [],
    }

    print(f"Fetching existing sources from {SOURCES_FILE}...")
    for s in load_sources(SOURCES_FILE):
        context["sources"].append(process_source(s, since, "existing"))

    candidates = load_candidates(CANDIDATES_FILE)
    if candidates:
        print(f"\nFetching {len(candidates)} candidate(s) from {CANDIDATES_FILE}...")
        for c in candidates:
            context["candidates"].append(process_source(c, since, "candidate"))
    else:
        print(f"\nNo candidates.yaml entries found — skipping candidate pre-fetch.")

    OUTPUT_FILE.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
    total_sources = len(context["sources"])
    total_candidates = len(context["candidates"])
    print(f"\nWritten to {OUTPUT_FILE} ({total_sources} sources, {total_candidates} candidates)")
    print("Now run /curate or /scan-sources in Claude Code.")


if __name__ == "__main__":
    main()
