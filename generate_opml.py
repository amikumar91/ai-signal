#!/usr/bin/env python3
"""
generate_opml.py — generates sources.opml from sources.yaml

Usage:
    python generate_opml.py
    python generate_opml.py --output custom.opml

Output is a valid OPML 2.0 file importable into Feedly, NetNewsWire,
Reeder, Inoreader, and any other RSS reader that supports OPML.
"""

import argparse
import sys
from datetime import datetime, timezone
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


def load_sources(path: Path) -> list[dict]:
    with path.open() as f:
        data = yaml.safe_load(f)
    return data["sources"]


def build_opml(sources: list[dict]) -> Element:
    root = Element("opml", version="2.0")

    head = SubElement(root, "head")
    SubElement(head, "title").text = "AI Signal — Curated AI sources"
    SubElement(head, "dateCreated").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )
    SubElement(head, "ownerName").text = "AI Signal"
    SubElement(head, "ownerEmail").text = "contribute via GitHub PR"
    SubElement(head, "docs").text = "https://github.com/amikumar91/ai-signal"

    body = SubElement(root, "body")

    # Group by type, in defined order
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
                continue  # skip sources without RSS

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


def main():
    parser = argparse.ArgumentParser(description="Generate OPML from sources.yaml")
    parser.add_argument(
        "--input",
        default="sources.yaml",
        help="Input YAML file (default: sources.yaml)",
    )
    parser.add_argument(
        "--output",
        default="sources.opml",
        help="Output OPML file (default: sources.opml)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    sources = load_sources(input_path)
    root = build_opml(sources)
    indent(root, space="  ")

    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root, encoding="unicode"
    ).encode("utf-8")

    output_path.write_bytes(xml_bytes)

    total = len(sources)
    with_rss = sum(1 for s in sources if s.get("rss"))
    print(f"Generated {output_path}")
    print(f"  {total} sources total, {with_rss} with RSS feeds")
    print(f"  Import {output_path} into Feedly, Reeder, NetNewsWire, or Inoreader")


if __name__ == "__main__":
    main()
