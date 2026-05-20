import importlib
import json
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── load_sources ──────────────────────────────────────────────────────────────

def test_load_sources_returns_list(tmp_path):
    yaml_content = """
sources:
  - name: Test Blog
    url: https://test.com
    rss: https://test.com/feed.xml
    type: individual
    depth: deep
    audience: [researcher]
    tags: [test]
    activity: active
    last_checked: 2026-05
"""
    yaml_file = tmp_path / "sources.yaml"
    yaml_file.write_text(yaml_content)
    from curate import load_sources
    sources = load_sources(yaml_file)
    assert len(sources) == 1
    assert sources[0]["name"] == "Test Blog"
    assert sources[0]["rss"] == "https://test.com/feed.xml"


def test_load_sources_preserves_landmark_posts(tmp_path):
    yaml_content = """
sources:
  - name: Test Blog
    url: https://test.com
    rss: https://test.com/feed.xml
    type: individual
    depth: deep
    audience: [researcher]
    tags: [test]
    activity: active
    last_checked: 2026-05
    landmark_posts:
      - title: "A great post"
        url: https://test.com/great
        why: "Because it is great"
"""
    yaml_file = tmp_path / "sources.yaml"
    yaml_file.write_text(yaml_content)
    from curate import load_sources
    sources = load_sources(yaml_file)
    assert sources[0]["landmark_posts"][0]["title"] == "A great post"


# ── fetch_recent_entries ──────────────────────────────────────────────────────

def _make_mock_entry(title, url, days_ago, summary="Content"):
    entry = MagicMock()
    entry.title = title
    entry.link = url
    pub = datetime.now(timezone.utc) - timedelta(days=days_ago)
    entry.published_parsed = (pub.year, pub.month, pub.day, 0, 0, 0, 0, 0, 0)
    entry.updated_parsed = None
    entry.summary = summary
    return entry


def test_fetch_recent_entries_includes_recent_post():
    mock_feed = MagicMock()
    mock_feed.entries = [_make_mock_entry("New Post", "https://test.com/new", days_ago=5)]
    with patch("feedparser.parse", return_value=mock_feed):
        from curate import fetch_recent_entries
        since = datetime.now(timezone.utc) - timedelta(days=90)
        result = fetch_recent_entries("https://test.com/feed.xml", since)
    assert len(result) == 1
    assert result[0]["title"] == "New Post"
    assert result[0]["url"] == "https://test.com/new"


def test_fetch_recent_entries_excludes_old_post():
    mock_feed = MagicMock()
    mock_feed.entries = [_make_mock_entry("Old Post", "https://test.com/old", days_ago=120)]
    with patch("feedparser.parse", return_value=mock_feed):
        from curate import fetch_recent_entries
        since = datetime.now(timezone.utc) - timedelta(days=90)
        result = fetch_recent_entries("https://test.com/feed.xml", since)
    assert result == []


def test_fetch_recent_entries_handles_network_error():
    with patch("feedparser.parse", side_effect=Exception("network error")):
        from curate import fetch_recent_entries
        since = datetime.now(timezone.utc) - timedelta(days=90)
        result = fetch_recent_entries("https://test.com/feed.xml", since)
    assert result == []


def test_fetch_recent_entries_caps_at_twenty():
    entries = [_make_mock_entry(f"Post {i}", f"https://t.com/{i}", days_ago=1) for i in range(30)]
    mock_feed = MagicMock()
    mock_feed.entries = entries
    with patch("feedparser.parse", return_value=mock_feed):
        from curate import fetch_recent_entries
        since = datetime.now(timezone.utc) - timedelta(days=90)
        result = fetch_recent_entries("https://test.com/feed.xml", since)
    assert len(result) <= 20


def test_fetch_recent_entries_truncates_summary():
    long_summary = "x" * 500
    mock_feed = MagicMock()
    mock_feed.entries = [_make_mock_entry("Post", "https://t.com/p", days_ago=1, summary=long_summary)]
    with patch("feedparser.parse", return_value=mock_feed):
        from curate import fetch_recent_entries
        since = datetime.now(timezone.utc) - timedelta(days=90)
        result = fetch_recent_entries("https://test.com/feed.xml", since)
    assert len(result[0]["summary"]) <= 300


# ── main / output ─────────────────────────────────────────────────────────────

def test_main_writes_valid_json(tmp_path, monkeypatch):
    yaml_content = """
sources:
  - name: Test Blog
    url: https://test.com
    rss: https://test.com/feed.xml
    type: individual
    depth: deep
    audience: [researcher]
    tags: [test]
    activity: active
    last_checked: 2026-05
"""
    (tmp_path / "sources.yaml").write_text(yaml_content)
    output_file = tmp_path / "_curate_context.json"
    monkeypatch.chdir(tmp_path)

    mock_feed = MagicMock()
    mock_feed.entries = []

    with patch("feedparser.parse", return_value=mock_feed):
        import curate
        importlib.reload(curate)
        curate.OUTPUT_FILE = output_file
        curate.main()

    data = json.loads(output_file.read_text())
    assert "sources" in data
    assert data["sources"][0]["name"] == "Test Blog"
    assert "generated_at" in data
    assert "lookback_days" in data
