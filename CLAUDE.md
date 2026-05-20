# AI Signal — Claude Code Instructions

## Project overview

AI Signal is a curated reading list for the AI field. The canonical data lives in
`sources.yaml`. Everything else is generated from it:

- `generate_opml.py` → `sources.opml` (RSS reader import file)
- `index.html` — static filterable site, deployed to GitHub Pages on push

**After any edit to `sources.yaml`:** always run `python generate_opml.py` and
commit both `sources.yaml` and `sources.opml` together.

---

## Curation commands

Two slash commands handle all curation. Both use **web search** as the primary
signal — not RSS, which is unreliable. Both edit `sources.yaml` directly so
the user can review with `git diff`.

### /scan-sources

Checks every existing source for recent activity via web search.
Updates `activity` and `last_checked` fields in `sources.yaml` in-place.
Use this for a quick activity pass without full discovery.

### /curate

Full curation pass:
1. Scans existing sources for activity changes (same as /scan-sources)
2. Identifies landmark-worthy recent posts on existing sources
3. Evaluates any entries in `candidates.yaml`
4. Discovers new source candidates via web search
5. Edits `sources.yaml` directly — new sources marked `# PROPOSED`

After either command:
```bash
git diff sources.yaml     # review all changes
python generate_opml.py
git add sources.yaml sources.opml
git commit -m "curate: YYYY-MM-DD"
git push
```

---

## candidates.yaml

A queue for URLs you want evaluated during the next `/curate` run. Add a URL,
run `/curate`, Claude evaluates and either adds it to `sources.yaml` or skips it.
Remove entries after evaluation.

---

## curate.py (optional pre-fetch)

`python curate.py` fetches RSS entries for existing sources and any candidates
in `candidates.yaml`, writing `_curate_context.json`. This is supplementary —
**zero posts in the output does not mean a source is inactive** (RSS often fails).
Always verify activity via web search.

```bash
python -m pip install pyyaml feedparser
python curate.py
```

---

## Contributing workflow

See `contributing.md` for the full guide. Quick reference:

1. Edit `sources.yaml`
2. `python generate_opml.py`
3. `git add sources.yaml sources.opml && git commit`
4. Push — GitHub Pages redeploys automatically
