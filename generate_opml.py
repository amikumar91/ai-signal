#!/usr/bin/env python3
"""
generate_opml.py — generates sources.opml and updates index.html from sources.yaml

Usage:
    python generate_opml.py

Outputs:
    sources.opml   — importable into Feedly, Reeder, NetNewsWire, Inoreader
    index.html     — SOURCES block rewritten to match sources.yaml
"""

import json
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, tostring

try:
    import yaml
except ImportError:
    print("PyYAML not found. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

TYPE_LABELS = {
    "lab": "Labs & Research",
    "individual": "Individuals",
    "applied": "Applied / Company Blogs",
    "systems": "Systems & Infrastructure",
    "paper-explainer": "Paper Explainers",
    "news": "News & Digests",
}

TYPE_ORDER = ["lab", "individual", "systems", "paper-explainer", "applied", "news"]

# Sentinels that delimit the auto-generated block inside index.html
INDEX_START = "// ── Data (generated from sources.yaml)"
INDEX_END   = "// ── Config"


def load_sources(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["sources"]


# ── OPML ─────────────────────────────────────────────────────────────────────

def build_opml(sources: list[dict]) -> Element:
    root = Element("opml", version="2.0")

    head = SubElement(root, "head")
    SubElement(head, "title").text = "AI Signal — Curated AI sources"
    SubElement(head, "ownerName").text = "AI Signal"
    SubElement(head, "ownerEmail").text = "contribute via GitHub PR"
    SubElement(head, "docs").text = "https://github.com/amikumar91/ai-signal"

    body = SubElement(root, "body")

    by_type: dict[str, list[dict]] = {t: [] for t in TYPE_ORDER}
    for source in sources:
        t = source.get("type", "applied")
        if t in by_type:
            by_type[t].append(source)

    for type_key in TYPE_ORDER:
        group = by_type[type_key]
        if not group:
            continue

        label = TYPE_LABELS.get(type_key, type_key)
        folder = SubElement(body, "outline", text=label, title=label)

        for s in group:
            rss = s.get("rss")
            if not rss:
                continue

            tags = ", ".join(s.get("tags", []))
            audience = ", ".join(s.get("audience", []))
            description = f"[{s.get('depth', '')}] [{audience}] {tags}"

            SubElement(
                folder,
                "outline",
                type="rss",
                text=s["name"],
                title=s["name"],
                xmlUrl=rss,
                htmlUrl=s.get("url", rss),
                description=description,
            )

    return root


def write_opml(sources: list[dict], output_path: Path) -> None:
    root = build_opml(sources)
    indent(root, space="  ")
    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root, encoding="unicode"
    ).encode("utf-8")
    output_path.write_bytes(xml_bytes)


# ── index.html SOURCES block ──────────────────────────────────────────────────

def _js_str(value: str) -> str:
    """Return a double-quoted JS string literal with minimal escaping."""
    return json.dumps(value, ensure_ascii=False)


def _js_str_array(items: list[str]) -> str:
    return "[" + ",".join(_js_str(i) for i in items) + "]"


def _source_to_js(s: dict) -> str:
    lines = []
    lines.append("  {")

    name     = _js_str(s.get("name", ""))
    url      = _js_str(s.get("url", ""))
    rss      = _js_str(s.get("rss") or "")
    stype    = _js_str(s.get("type", ""))
    depth    = _js_str(s.get("depth", ""))
    audience = _js_str_array(s.get("audience", []))
    tags     = _js_str_array(s.get("tags", []))
    activity = _js_str(s.get("activity", ""))
    checked  = _js_str(s.get("last_checked", ""))

    lines.append(f"    name: {name}, url: {url},")
    lines.append(f"    rss: {rss}, type: {stype}, depth: {depth},")
    lines.append(f"    audience: {audience}, tags: {tags},")
    lines.append(f"    activity: {activity}, last_checked: {checked},")

    landmarks = s.get("landmark_posts") or []
    if landmarks:
        lm_parts = []
        for lm in landmarks:
            t = _js_str(lm.get("title", ""))
            u = _js_str(lm.get("url", ""))
            w = _js_str(lm.get("why", ""))
            lm_parts.append(f"{{title:{t}, url:{u}, why:{w}}}")
        lines.append(f"    landmarks: [{', '.join(lm_parts)}]")
    else:
        lines.append("    landmarks: []")

    lines.append("  }")
    return "\n".join(lines)


def build_sources_block(sources: list[dict]) -> str:
    sep = INDEX_START + " " + "─" * (79 - len(INDEX_START) - 1)
    entries = ",\n".join(_source_to_js(s) for s in sources)
    return f"{sep}\nconst SOURCES = [\n{entries},\n];\n"


def update_index_html(sources: list[dict], index_path: Path) -> bool:
    if not index_path.exists():
        print(f"  Skipped index.html update ({index_path} not found)", file=sys.stderr)
        return False

    html = index_path.read_text(encoding="utf-8")

    start_pos = html.find(INDEX_START)
    end_pos   = html.find(INDEX_END, start_pos)

    if start_pos == -1 or end_pos == -1:
        print("  Skipped index.html update (sentinel comments not found)", file=sys.stderr)
        return False

    new_block = build_sources_block(sources)
    updated = html[:start_pos] + new_block + "\n" + html[end_pos:]
    index_path.write_text(updated, encoding="utf-8")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    sources_path = Path("sources.yaml")
    opml_path    = Path("sources.opml")
    index_path   = Path("index.html")

    if not sources_path.exists():
        print(f"Error: {sources_path} not found", file=sys.stderr)
        sys.exit(1)

    sources = load_sources(sources_path)

    write_opml(sources, opml_path)
    html_updated = update_index_html(sources, index_path)

    total     = len(sources)
    with_rss  = sum(1 for s in sources if s.get("rss"))
    landmarks = sum(len(s.get("landmark_posts") or []) for s in sources)

    print(f"Generated {opml_path}")
    print(f"  {total} sources, {with_rss} with RSS, {landmarks} landmark posts")
    if html_updated:
        print(f"Updated  {index_path}  (SOURCES block rewritten)")
    print(f"  Import {opml_path} into Feedly, Reeder, NetNewsWire, or Inoreader")


if __name__ == "__main__":
    main()
