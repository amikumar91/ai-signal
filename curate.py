#!/usr/bin/env python3
"""
curate.py — Gather RSS data for the AI Signal curation agent.

Usage:
    python -m pip install pyyaml feedparser
    python curate.py

Outputs _curate_context.json (gitignored), then open Claude Code and say:
    run curation
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


def load_sources(path: Path) -> list[dict]:
    with path.open() as f:
        return yaml.safe_load(f)["sources"]


def fetch_recent_entries(rss_url: str, since: datetime) -> list[dict]:
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


def main():
    sources = load_sources(Path("sources.yaml"))
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    context = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": LOOKBACK_DAYS,
        "sources": [],
    }

    for s in sources:
        print(f"Fetching: {s['name']} ...", end=" ", flush=True)
        rss = s.get("rss")
        recent = []
        if rss:
            recent = fetch_recent_entries(rss, since)
            print(f"{len(recent)} recent posts")
        else:
            print("no RSS")

        context["sources"].append({
            "name": s["name"],
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
        })

    OUTPUT_FILE.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
    total = len(context["sources"])
    print(f"\nContext written to {OUTPUT_FILE} ({total} sources)")
    print("Now open Claude Code in this directory and say: run curation")


if __name__ == "__main__":
    main()
