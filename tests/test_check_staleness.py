import importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import requests

_SCRIPT = Path(__file__).resolve().parent.parent / ".github" / "scripts" / "check_staleness.py"
_spec = importlib.util.spec_from_file_location("check_staleness", _SCRIPT)
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)


def _rss(*dates: datetime) -> bytes:
    items = "".join(
        f"<item><title>p{i}</title><link>https://x.com/{i}</link>"
        f"<pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate></item>"
        for i, d in enumerate(dates)
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>{items}</channel></rss>'.encode()


def _resp(status=200, content=b""):
    r = MagicMock()
    r.status_code = status
    r.content = content
    return r


# ── check_feed ────────────────────────────────────────────────────────────────

def test_check_feed_returns_newest_entry_even_if_unsorted():
    old = datetime(2026, 1, 1, tzinfo=timezone.utc)
    new = datetime(2026, 9, 1, tzinfo=timezone.utc)
    with patch.object(cs.requests, "get", return_value=_resp(200, _rss(old, new))):
        status, latest, _ = cs.check_feed("https://x.com/feed")
    assert status == cs.OK
    assert latest == new


def test_check_feed_sends_user_agent():
    with patch.object(cs.requests, "get", return_value=_resp(200, _rss(datetime.now(timezone.utc)))) as get:
        cs.check_feed("https://x.com/feed")
    assert "ai-signal" in get.call_args.kwargs["headers"]["User-Agent"]


def test_check_feed_classifies_404_as_not_found():
    with patch.object(cs.requests, "get", return_value=_resp(404)):
        assert cs.check_feed("https://x.com/feed")[0] == cs.NOT_FOUND


def test_check_feed_classifies_403_as_blocked():
    with patch.object(cs.requests, "get", return_value=_resp(403)):
        assert cs.check_feed("https://x.com/feed")[0] == cs.BLOCKED


def test_check_feed_classifies_html_page_as_broken():
    with patch.object(cs.requests, "get", return_value=_resp(200, b"<html><body>hi</body></html>")):
        assert cs.check_feed("https://x.com/feed")[0] == cs.BROKEN


def test_check_feed_handles_network_error():
    with patch.object(cs.requests, "get", side_effect=requests.ConnectionError()):
        assert cs.check_feed("https://x.com/feed")[0] == cs.BROKEN


# ── thresholds / main ─────────────────────────────────────────────────────────

def _run_main(sources, latest):
    with patch.object(cs, "load_sources", return_value=sources), \
         patch.object(cs, "check_feed", return_value=(cs.OK, latest, "")), \
         patch.object(cs, "sync_issue") as sync:
        cs.main()
    return sync.call_args.args


def _src(activity):
    return {"name": "S", "url": "https://s.com", "rss": "https://s.com/feed", "activity": activity}


def test_slow_source_not_flagged_at_120_days():
    latest = datetime.now(timezone.utc) - timedelta(days=120)
    assert _run_main([_src("slow")], latest) == (None, None)


def test_active_source_flagged_at_120_days():
    latest = datetime.now(timezone.utc) - timedelta(days=120)
    title, body = _run_main([_src("active")], latest)
    assert title.startswith("Staleness check: 1 stale")
    assert "`slow`" in body


def test_slow_source_flagged_past_18_months_suggests_archived():
    latest = datetime.now(timezone.utc) - timedelta(days=600)
    title, body = _run_main([_src("slow")], latest)
    assert "1 stale" in title
    assert "`archived`" in body


def test_archived_source_not_checked():
    with patch.object(cs, "load_sources", return_value=[_src("archived")]), \
         patch.object(cs, "check_feed") as check, \
         patch.object(cs, "sync_issue"):
        cs.main()
    check.assert_not_called()


def test_blocked_only_does_not_count_as_error():
    s = _src("active")
    title, body = cs.build_report([], [], [(s, "HTTP 403")], [], datetime.now(timezone.utc))
    assert "0 feed errors" in title
    assert "Could not verify" in body


# ── sync_issue ────────────────────────────────────────────────────────────────

def test_sync_updates_newest_and_closes_duplicates():
    issues = [{"number": 23, "html_url": "u23"}, {"number": 22, "html_url": "u22"}, {"number": 1, "html_url": "u1"}]
    with patch.object(cs, "TOKEN", "t"), \
         patch.object(cs, "open_staleness_issues", return_value=issues), \
         patch.object(cs, "_gh") as gh, \
         patch.object(cs, "close_issue") as close:
        cs.sync_issue("T", "B")
    gh.assert_called_once_with("PATCH", "/issues/23", json={"title": "T", "body": "B"})
    assert [c.args[0] for c in close.call_args_list] == [22, 1]


def test_sync_creates_issue_when_none_open():
    with patch.object(cs, "TOKEN", "t"), \
         patch.object(cs, "open_staleness_issues", return_value=[]), \
         patch.object(cs, "_gh", return_value={"number": 5, "html_url": "u5"}) as gh, \
         patch.object(cs, "close_issue") as close:
        cs.sync_issue("T", "B")
    assert gh.call_args.args[:2] == ("POST", "/issues")
    close.assert_not_called()


def test_sync_closes_all_when_fresh():
    issues = [{"number": 23, "html_url": "u23"}]
    with patch.object(cs, "TOKEN", "t"), \
         patch.object(cs, "open_staleness_issues", return_value=issues), \
         patch.object(cs, "close_issue") as close:
        cs.sync_issue(None, None)
    assert close.call_args.args[0] == 23


# ── generate_opml determinism ─────────────────────────────────────────────────

def test_opml_output_is_deterministic(tmp_path):
    from generate_opml import write_opml
    sources = [{"name": "S", "url": "https://s.com", "rss": "https://s.com/feed", "type": "lab",
                "depth": "deep", "audience": ["researcher"], "tags": ["t"]}]
    a, b = tmp_path / "a.opml", tmp_path / "b.opml"
    write_opml(sources, a)
    write_opml(sources, b)
    assert a.read_bytes() == b.read_bytes()
